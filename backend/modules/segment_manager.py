"""
segment_manager.py

Extracts suspect answer segments from a full interview video/audio.
Uses speaker diarization and OpenAI Whisper for transcription.
Identifies both suspect and interviewer speakers, links questions to answers.

Class:
    SegmentManager
        get_suspect_segments(video_path, audio_path, suspect_label=None)
"""

import os
import tempfile
import subprocess
from pydub import AudioSegment
from speaker_diarizer import SpeakerDiarizer
import whisper


class SegmentManager:
    """Handles speaker separation and answer segmentation."""

    def __init__(self, device="cpu"):
        self.diarizer = SpeakerDiarizer(device=device)
        self.whisper_model = whisper.load_model("base")

    def get_suspect_segments(self, audio_path, suspect_label=None):
        """Identify suspect speaking turns, linked to interviewer questions.

        Long suspect responses (>15s) are split into smaller sub-segments
        using silence-based VAD for more granular analysis.

        Returns:
            list of dicts: [{'start': float, 'end': float, 'audio_file': str,
                            'question': dict or None}, ...]
            Each question dict: {'start': float, 'end': float, 'text': str}
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio not found: {audio_path}")

        # Step 1: Diarize
        segments = self.diarizer.diarize(audio_path)

        # Step 2: Identify suspect and interviewer speaker labels
        speaker_durations = {}
        for seg in segments:
            speaker = seg['speaker']
            speaker_durations[speaker] = speaker_durations.get(speaker, 0) + seg['end'] - seg['start']

        if not speaker_durations:
            print("No speakers found.")
            return []

        if suspect_label is None:
            suspect_label = max(speaker_durations, key=speaker_durations.get)
        print(f"Suspect speaker label: {suspect_label}")

        # Identify interviewer (most-talkative non-suspect speaker)
        interviewer_label = None
        other_speakers = [s for s in speaker_durations if s != suspect_label]
        if other_speakers:
            interviewer_label = max(other_speakers, key=lambda s: speaker_durations[s])
            print(f"Interviewer speaker label: {interviewer_label}")

        suspect_segments = [seg for seg in segments if seg['speaker'] == suspect_label]
        if not suspect_segments:
            print(f"No segments found for speaker {suspect_label}.")
            return []

        interviewer_segments = [seg for seg in segments if seg['speaker'] == interviewer_label] if interviewer_label else []
        interviewer_merged = self._merge_segments(interviewer_segments, gap=0.5) if interviewer_segments else []

        # Merge nearby suspect turns, then check for the preceding question
        merged = self._merge_segments(suspect_segments, gap=0.5)

        full_audio = AudioSegment.from_file(audio_path)
        result = []

        # Pre-compute question text for all interviewer merged blocks
        question_texts = {}
        if interviewer_merged:
            for qi, (q_start, q_end) in enumerate(interviewer_merged):
                q_text = self._transcribe_block(full_audio, q_start, q_end, f"_question_{qi}")
                if len(q_text) >= 3:
                    question_texts[(q_start, q_end)] = q_text

        for i, (start, end) in enumerate(merged):
            duration_sec = round(end - start, 2)
            if duration_sec < 1.0:
                print(f"  Skipping segment {i+1} ({start:.1f}s-{end:.1f}s) — too short ({duration_sec}s)")
                continue

            # Find closest preceding interviewer question
            question_info = None
            closest_q = None
            for q_start, q_end in interviewer_merged:
                if q_end <= start:
                    if closest_q is None or q_start > closest_q[0]:
                        closest_q = (q_start, q_end)

            if closest_q:
                q_start, q_end = closest_q
                q_text = question_texts.get((q_start, q_end), "")
                if q_text:
                    print(f"  Question {i+1} ({q_start:.1f}s-{q_end:.1f}s): \"{q_text[:80]}{'...' if len(q_text) > 80 else ''}\"")
                else:
                    print(f"  Question {i+1} ({q_start:.1f}s-{q_end:.1f}s): [no speech detected]")
                question_info = {'start': q_start, 'end': q_end, 'text': q_text}
            else:
                print(f"  Segment {i+1} ({start:.1f}s-{end:.1f}s): [no preceding question, using default]")

            # Split long segments using VAD
            sub_segments = self._split_by_silence(full_audio, start, end, max_duration=15.0)

            for si, (sub_start, sub_end) in enumerate(sub_segments):
                # Double-check sub-segment has energy (skip near-silence)
                sub_duration = sub_end - sub_start
                sub_audio_check = full_audio[sub_start * 1000:sub_end * 1000]
                sub_rms = sub_audio_check.rms
                if sub_rms < 50 and si > 0:
                    print(f"  Sub-segment {si+1} ({sub_start:.1f}s-{sub_end:.1f}s) low energy ({sub_rms:.1f}), skipping.")
                    continue
                sub_dur = round(sub_end - sub_start, 2)
                sub_file = os.path.join(tempfile.gettempdir(), f"_segment_{i+1}_{si+1}.wav")
                sub_audio = full_audio[sub_start*1000:sub_end*1000]
                sub_audio.export(sub_file, format="wav")

                result.append({
                    'start': sub_start,
                    'end': sub_end,
                    'audio_file': os.path.abspath(sub_file),
                    'question': question_info
                })

        print(f"Extracted {len(result)} suspect answer segments after VAD split.")
        linked = sum(1 for r in result if r['question'] is not None and r['question'].get('text'))
        if interviewer_label:
            print(f"  Linked {linked}/{len(result)} to interviewer questions.")
        return result

    def _transcribe_block(self, full_audio, start_sec, end_sec, label):
        """Transcribe a block of audio; returns text or empty string on failure."""
        dur = end_sec - start_sec
        if dur < 0.3:
            return ""
        temp = os.path.join(tempfile.gettempdir(), f"{label}.wav")
        try:
            block = full_audio[start_sec*1000:end_sec*1000]
            block.export(temp, format="wav")
            res = self.whisper_model.transcribe(temp, task="transcribe")
            text = res['text'].strip()
            if len(text) < 3:
                text = ""
            return text
        except Exception:
            return ""
        finally:
            try:
                os.remove(temp)
            except Exception:
                pass

    def _split_by_silence(self, full_audio, start_sec, end_sec, max_duration=15.0, min_duration=2.0):
        """Split a long segment into sub-segments at silence boundaries.

        Uses pydub's detect_nonsilent to find natural pause points.
        Returns list of (start_sec, end_sec) tuples.
        """
        duration = end_sec - start_sec
        if duration <= max_duration:
            return [(start_sec, end_sec)]

        segment_ms = full_audio[start_sec * 1000:end_sec * 1000]
        from pydub.silence import detect_nonsilent
        nonsilent = detect_nonsilent(segment_ms, min_silence_len=400, silence_thresh=-40)

        if not nonsilent:
            return [(start_sec, end_sec)]

        # Convert ms offsets to absolute timestamps
        boundaries = [start_sec]
        for ns_start_ms, ns_end_ms in nonsilent:
            abs_start = start_sec + ns_start_ms / 1000.0
            abs_end = start_sec + ns_end_ms / 1000.0
            if abs_end - abs_start >= min_duration:
                if abs_start - boundaries[-1] >= min_duration:
                    boundaries.append(abs_start)
                boundaries.append(abs_end)

        if len(boundaries) <= 1:
            return [(start_sec, end_sec)]

        # Merge short boundary gaps with neighbors
        result = []
        i = 0
        while i < len(boundaries) - 1:
            seg_len = boundaries[i + 1] - boundaries[i]
            if seg_len >= min_duration:
                result.append((boundaries[i], boundaries[i + 1]))
                i += 1
            else:
                if result:
                    prev_start, _ = result.pop()
                    result.append((prev_start, boundaries[i + 1]))
                elif i + 2 < len(boundaries):
                    result.append((boundaries[i], boundaries[i + 2]))
                    i += 2
                    continue
                else:
                    result.append((boundaries[i], boundaries[i + 1]))
                i += 1

        return result if result else [(start_sec, end_sec)]

    def _merge_segments(self, segs, gap=0.5):
        if not segs:
            return []
        segs = sorted(segs, key=lambda x: x['start'])
        merged = []
        cur_start = segs[0]['start']
        cur_end = segs[0]['end']
        for s in segs[1:]:
            if s['start'] - cur_end <= gap:
                cur_end = max(cur_end, s['end'])
            else:
                merged.append((cur_start, cur_end))
                cur_start = s['start']
                cur_end = s['end']
        merged.append((cur_start, cur_end))
        return merged
