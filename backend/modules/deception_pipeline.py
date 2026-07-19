"""
deception_pipeline.py

Master orchestrator for the Deceptron deception detection system.
Takes a video (or video+audio), extracts suspect answer segments,
runs all analyzers per segment, fuses results, and generates a
comprehensive JSON report with natural‑language reasoning.

Output:
    - Full annotated videos (one per module) in the "results" directory.
    - A 2x2 combined presentation video (eye, emotion, hand, lip) with audio.
    - Per‑segment deception report JSON in the "reports" directory.
"""

import os
import sys

# Disable tqdm progress bars to fix [WinError 6] The handle is invalid on Windows
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

# Fix for PyTorch 2.6+: Monkey-patch torch.load to force weights_only=False
# This allows pyannote and other modules to load custom classes safely from local files.
try:
    import torch
    # Allowlist common Pyannote and Torch globals to satisfy the unpickler
    if hasattr(torch, 'serialization') and hasattr(torch.serialization, 'add_safe_globals'):
        try:
            from pyannote.audio.core.task import Specifications
            torch.serialization.add_safe_globals([torch.torch_version.TorchVersion, Specifications])
        except Exception: 
            # If import fails, we still have the monkey-patch below
            pass

    _orig_torch_load = torch.load
    def _patched_torch_load(*args, **kwargs):
        # Force weights_only to False to avoid unpickling errors with custom model classes
        kwargs['weights_only'] = False
        return _orig_torch_load(*args, **kwargs)
    torch.load = _patched_torch_load
except Exception:
    pass

import argparse
import json
import subprocess
import tempfile
import traceback
import cv2
import numpy as np
from collections import Counter
from typing import Dict, List, Any, Optional
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import project modules (assumed to be in the same directory)
try:
    from speaker_diarizer import SpeakerDiarizer
    from segment_manager import SegmentManager
    from forensic_voice_analyzer import ForensicVoiceAnalyzer
    from eye_gaze_module import EyeGazeAnalyzer
    from lip_jaw_module import LipJawAnalyzer
    from head_pose_module import HeadPoseAnalyzer
    from hand_face_touch_module import HandFaceTouchAnalyzer
    from asymmetry_module import AsymmetryAnalyzer
    from emotion_detection_module import EmotionAnalyzer
    from nlp_deception_module import NLPDeceptionAnalyzer
    from fusion_engine import FusionEngine
    from reasoning_engine import ReasoningEngine
except ImportError as e:
    print(f"Missing module: {e}")
    print("Make sure all project .py files are in the same directory.")
    sys.exit(1)


class DeceptionPipeline:
    """Orchestrates the full multi‑modal deception detection workflow."""

    def __init__(self, report_dir: str = "reports", video_dir: str = "results"):
        self.report_dir = report_dir
        self.video_dir = video_dir
        os.makedirs(self.report_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)

        # Initialize all analyzers
        print("Initializing analyzers...")
        
        # Verify ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
            print("FFmpeg detected successfully.")
        except Exception:
            print("CRITICAL ERROR: FFmpeg is not installed or not in PATH. Pipeline will fail.")
            raise RuntimeError("FFmpeg not found. Please install FFmpeg to run the deception pipeline.")

        try:
            self.voice_analyzer = ForensicVoiceAnalyzer()
            self.eye_analyzer = EyeGazeAnalyzer()
            self.lip_analyzer = LipJawAnalyzer()
            self.head_analyzer = HeadPoseAnalyzer()
            self.hand_analyzer = HandFaceTouchAnalyzer()
            self.asymmetry_analyzer = AsymmetryAnalyzer()
            self.emotion_analyzer = EmotionAnalyzer()
            self.nlp_analyzer = NLPDeceptionAnalyzer()
            self.fusion_engine = FusionEngine()
            self.reasoning_engine = ReasoningEngine()
            self.segment_manager = SegmentManager()
        except Exception as e:
            print(f"Error loading analyzers: {e}")
            traceback.print_exc()
            raise e
            
        print("All analyzers loaded successfully.")

    def process(self, video_path: str, audio_path: Optional[str] = None,
                question_context: str = ""):
        """Run the full pipeline on a video file.

        Args:
            video_path: Path to interrogation video (must contain suspect).
            audio_path: If provided, uses this audio file; otherwise extracts from video.
            question_context: Optional interview question (default empty).

        Returns:
            Path to the generated JSON report.
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"\n{'='*60}")
        print(f"  DECEPTRON DECEPTION PIPELINE - Session {session_id}")
        print(f"{'='*60}\n")

        # ------------------------------------------------------------------
        # 1. Handle audio: extract from video if needed
        # ------------------------------------------------------------------
        if audio_path is None:
            print("Extracting audio from video...")
            audio_path = self._extract_audio(video_path)
            if not audio_path:
                print("Failed to extract audio. Aborting.")
                return None
        else:
            print(f"Using provided audio: {audio_path}")

        # ------------------------------------------------------------------
        # 2. Generate full annotated videos (including emotion)
        # ------------------------------------------------------------------
        stem = os.path.splitext(os.path.basename(video_path))[0]
        self._generate_annotated_videos(video_path, stem)

        # ---- Combine selected videos into a 2x2 presentation video with audio ----
        self._create_combined_video(stem, audio_path)

        # ------------------------------------------------------------------
        # 3. Get suspect answer segments
        # ------------------------------------------------------------------
        print("\nRunning speaker diarization & segmentation...")
        segments = self.segment_manager.get_suspect_segments(audio_path)
        if not segments:
            print("No suspect segments found. Check audio content.")
            return None
        print(f"Found {len(segments)} suspect speaking segments.")

        # ------------------------------------------------------------------
        # 4. Get video FPS and total frames for time‑to‑frame conversion
        # ------------------------------------------------------------------
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        # ------------------------------------------------------------------
        # 4.5 Establish Behavioral Baseline (First 10 seconds)
        # ------------------------------------------------------------------
        print("\nEstablishing behavioral baseline (first 10 seconds)...")
        baseline_duration = min(10.0, total_frames / fps)
        baseline_end_frame = int(baseline_duration * fps)
        
        try:
            self.baseline_metrics = self._analyze_baseline(video_path, audio_path, baseline_end_frame)
            print("Baseline established successfully.")
        except Exception as e:
            print(f"Warning: Baseline analysis failed ({e}). Using defaults.")
            self.baseline_metrics = {}

        # ------------------------------------------------------------------
        # 5. Process each segment
        # ------------------------------------------------------------------
        segment_results = []
        previous_segments = []  # For cross-segment contradiction tracking
        full_timeline = []  # Deception score per second for the whole video
        video_duration_sec = total_frames / fps
        for i, seg in enumerate(segments):
            seg_id = f"SEG_{i+1:03d}"
            start_sec = seg['start']
            end_sec = seg['end']
            seg_audio = seg['audio_file']

            print(f"\n--- Processing Segment {seg_id}: {start_sec:.1f}s - {end_sec:.1f}s ---")

            # Convert time to frame numbers
            start_frame = max(1, int(start_sec * fps))
            end_frame = min(total_frames, int(end_sec * fps))

            # ---- Voice analysis ----
            voice_result = self.voice_analyzer.analyze_segment(
                seg_audio, 0, end_sec - start_sec, suppress_terminal=True)
            if voice_result is None:
                print("  Voice analysis failed, skipping segment.")
                continue
            voice_deception = voice_result.get('deception_analysis', {})
            voice_transcript_orig = voice_result.get('transcription_original', '')
            voice_transcript_en = voice_result.get('transcription_english', '')

            # Skip silent segments (silence detection in voice analyzer)
            voice_flags = voice_deception.get('triggered_flags', [])
            if 'silence' in voice_flags:
                print(f"  Segment is silent (no speech detected). Skipping.")
                continue
            if not voice_transcript_en and not voice_transcript_orig:
                print(f"  Empty transcription (silence/noise only). Skipping.")
                continue

            # ---- All face analyzers in parallel ----
            face_analyzers = {
                'eye': self.eye_analyzer,
                'lip': self.lip_analyzer,
                'head': self.head_analyzer,
                'asym': self.asymmetry_analyzer,
                'hand': self.hand_analyzer,
                'emotion': self.emotion_analyzer,
            }
            face_raw = {}
            with ThreadPoolExecutor(max_workers=6) as pool:
                futures = {
                    name: pool.submit(
                        a.process_video, video_path,
                        output_path=None,
                        start_frame=start_frame,
                        end_frame=end_frame,
                        verbose=False
                    )
                    for name, a in face_analyzers.items()
                }
                for name, future in futures.items():
                    try:
                        face_raw[name] = future.result()
                    except Exception as e:
                        print(f"  Face module '{name}' failed: {e}")
                        face_raw[name] = None

            # --- Eye gaze ---
            eye_data = face_raw.get('eye')
            if eye_data:
                gazes = [f['gaze'] for f in eye_data]
                avg_stab = (gazes.count('CENTER') / len(gazes) * 100) if gazes else 100
                dir_changes = sum(1 for i in range(1, len(eye_data))
                                  if eye_data[i]['gaze'] != eye_data[i-1]['gaze'])
                blink_count = eye_data[-1]['blink_count'] - eye_data[0]['blink_count'] if eye_data else 0
                blink_spike = blink_count > 2
                eye_summary = {
                    'gaze_stability': avg_stab,
                    'direction_changes': dir_changes,
                    'fixation_score': avg_stab,
                    'blink_rate_spike': blink_spike
                }
                eye_full = self.eye_analyzer.get_summary(eye_data)
            else:
                eye_summary = {'gaze_stability': 100, 'direction_changes': 0,
                               'fixation_score': 100, 'blink_rate_spike': False}
                eye_full = {}

            # --- Lip/jaw ---
            lip_data = face_raw.get('lip')
            if lip_data:
                avg_jaw = np.mean([f['jaw_tightness'] for f in lip_data])
                avg_oral = np.mean([f['oral_stress'] for f in lip_data])
                avg_tremor = np.mean([f['chin_tremor'] for f in lip_data])
                lip_dis = any(f['lip_disappear'] for f in lip_data)
                lip_summary = {
                    'jaw_tightness': avg_jaw,
                    'lip_compression': avg_oral,
                    'chin_tremor': avg_tremor,
                    'lip_disappear': lip_dis
                }
                lip_full = self.lip_analyzer.get_summary(lip_data)
            else:
                lip_summary = {'jaw_tightness': 0, 'lip_compression': 0,
                               'chin_tremor': 0, 'lip_disappear': False}
                lip_full = {}

            # --- Head pose ---
            head_data = face_raw.get('head')
            if head_data:
                avg_withdr = np.mean([f['withdrawal_score'] for f in head_data])
                avg_stiff = np.mean([f['stiffness_score'] for f in head_data])
                nodding = any(f['is_nodding'] for f in head_data)
                shaking = any(f['is_shaking'] for f in head_data)
                head_summary = {
                    'withdrawal_score': avg_withdr,
                    'stiffness': avg_stiff,
                    'is_nodding': nodding,
                    'is_shaking': shaking
                }
                head_full = self.head_analyzer.get_summary(head_data)
            else:
                head_summary = {'withdrawal_score': 0, 'stiffness': 0,
                                'is_nodding': False, 'is_shaking': False}
                head_full = {}

            # --- Asymmetry ---
            asym_data = face_raw.get('asym')
            if asym_data:
                avg_total_asym = np.mean([f['total_asym'] for f in asym_data])
                avg_mouth = np.mean([f['mouth_asym'] for f in asym_data])
                avg_brow = np.mean([f['brow_asym'] for f in asym_data])
                asym_summary = {
                    'total_asym': avg_total_asym,
                    'mouth_asym': avg_mouth,
                    'brow_asym': avg_brow
                }
                asym_full = self.asymmetry_analyzer.get_summary(asym_data)
            else:
                asym_summary = {'total_asym': 0, 'mouth_asym': 0, 'brow_asym': 0}
                asym_full = {}

            # --- Hand/face touch ---
            hand_data = face_raw.get('hand')
            if hand_data:
                touches = [f for f in hand_data if f['touches']]
                if touches:
                    max_dur = len(touches) / 30.0
                    all_regions = [r for f in touches for r in f['touches']]
                    best_region = max(set(all_regions), key=all_regions.count) if all_regions else 'NONE'
                    touch_summary = {
                        'touch_score': 100.0,
                        'touch_region': best_region,
                        'touch_duration': max_dur
                    }
                else:
                    touch_summary = {'touch_score': 0, 'touch_region': 'NONE', 'touch_duration': 0}
                hand_full = self.hand_analyzer.get_summary(hand_data)
            else:
                touch_summary = {'touch_score': 0, 'touch_region': 'NONE', 'touch_duration': 0}
                hand_full = {}

            # --- Emotion ---
            emotion_data = face_raw.get('emotion')
            if emotion_data:
                emotions = [f['emotion'] for f in emotion_data]
                if emotions:
                    dominant = Counter(emotions).most_common(1)[0][0]
                    changes = sum(1 for i in range(1, len(emotions)) if emotions[i] != emotions[i-1])
                    variance = min(100, (changes / len(emotions)) * 100)
                else:
                    dominant = 'Neutral'; variance = 50
                emotion_full = self.emotion_analyzer.get_summary(emotion_data)
            else:
                dominant = 'Neutral'; variance = 50
                emotion_full = {}

            emotion_summary = {
                'dominant_emotion': dominant,
                'emotion_variance': variance
            }

            # Assemble face data dict for fusion
            face_data = {
                'eye_gaze': eye_summary,
                'lip_jaw': lip_summary,
                'head_pose': head_summary,
                'asymmetry': asym_summary,
                'hand_touch': touch_summary,
                'emotion_timeline': emotion_summary
            }

            # ---- Extract question context for this segment ----
            q_text = ""
            if seg.get('question') and seg['question'].get('text'):
                q_text = seg['question']['text']
                print(f"  Question: \"{q_text[:100]}{'...' if len(q_text) > 100 else ''}\"")
            per_segment_context = q_text if q_text else (question_context if question_context else "What can you tell us about this situation?")

            # ---- NLP analysis with question context ----
            text_for_nlp = voice_transcript_en if voice_transcript_en else voice_transcript_orig
            nlp_result = self.nlp_analyzer.analyze(
                text=text_for_nlp,
                voice_stress=voice_deception.get('overall_deception_score', 0),
                question_context=per_segment_context,
                previous_segments=previous_segments
            )
            if nlp_result is None:
                nlp_result = {'overall_deception_score': 0, 'triggered_flags': []}

            # ---- Voice data for fusion ----
            voice_data = {
                'jitter': voice_result.get('micro_tremors', {}).get('jitter_local_percent', 0),
                'shimmer': voice_result.get('micro_tremors', {}).get('shimmer_local_percent', 0),
                'pitch_std': voice_result.get('fundamental_frequency', {}).get('f0_std_hz', 0),
                'pitch_variance_category': voice_result.get('fundamental_frequency', {}).get('stability_status', 'Stable'),
                'pause_ratio': voice_result.get('temporal_dynamics', {}).get('pause_ratio_percent', 0),
                'wpm': voice_result.get('temporal_dynamics', {}).get('speaking_rate_wpm', 0),
                'stress_category': voice_deception.get('stress_category', 'Low'),
                'deception_score': voice_deception.get('overall_deception_score', 0)
            }

            # ---- Fusion ----
            fusion_result = self.fusion_engine.fuse(
                face_data=face_data,
                voice_data=voice_data,
                nlp_data=nlp_result,
                timestamps=None
            )

            # ---- Advanced Analysis (Baseline comparison & Conflicts) ----
            # Detect mismatches (e.g. Happy face + Stressed voice)
            face_summary_for_conflict = {
                'eye_gaze': eye_summary,
                'emotion': emotion_summary
            }
            conflicts = self._detect_conflicts(face_summary_for_conflict, voice_deception)
            
            # Detect behavioral spikes relative to the first 10 seconds
            spikes = self._detect_spikes(
                {'face_cues': face_data, 'voice_stress': voice_deception}, 
                self.baseline_metrics
            )
            
            # Apply penalties based on conflicts and spikes
            if conflicts:
                fusion_result['final_deception_score'] = min(100, fusion_result['final_deception_score'] + (15 * len(conflicts)))
                for c in conflicts:
                    fusion_result['active_cues'].append({
                        'module': 'pipeline', 'cue': 'Conflict: ' + c, 
                        'severity': 100, 'timestamp': f"{start_sec:.2f}", 'duration': end_sec - start_sec
                    })
            
            if spikes:
                fusion_result['final_deception_score'] = min(100, fusion_result['final_deception_score'] + (10 * len(spikes)))
                for s in spikes:
                    fusion_result['active_cues'].append({
                        'module': 'pipeline', 'cue': 'Spike: ' + s, 
                        'severity': 100, 'timestamp': f"{start_sec:.2f}", 'duration': end_sec - start_sec
                    })

            # ---- Reasoning ----
            reasoning_input = {
                'text': text_for_nlp,
                'question': per_segment_context,
                'face_cues': face_data,
                'voice_stress': voice_data,
                'nlp_flags': nlp_result.get('triggered_flags', []),
                'nlp_analysis': nlp_result.get('summary', ''),
                'start_time': start_sec,
                'end_time': end_sec
            }
            reason = self.reasoning_engine.explain(reasoning_input)

            # ---- Compile segment result ----
            seg_result = {
                'segment_id': seg_id,
                'start_sec': start_sec,
                'end_sec': end_sec,
                'question': seg.get('question'),
                'transcript_original': voice_transcript_orig,
                'transcript_english': voice_transcript_en,
                'fusion': fusion_result,
                'reasoning': reason,
                'raw_scores': {
                    'voice_stress': voice_deception,
                    'eye_gaze': eye_full or eye_summary,
                    'lip_jaw': lip_full or lip_summary,
                    'head_pose': head_full or head_summary,
                    'asymmetry': asym_full or asym_summary,
                    'hand_touch': hand_full or touch_summary,
                    'emotion': emotion_full or emotion_summary,
                    'nlp': nlp_result
                }
            }
            segment_results.append(seg_result)

            # Track this segment for cross-segment contradiction detection
            previous_segments.append({
                'transcript_original': voice_transcript_orig,
                'transcript_english': voice_transcript_en,
                'question': seg.get('question'),
            })

            print(f"  → Deception Score: {fusion_result['final_deception_score']:.1f}% "
                  f"({fusion_result['confidence_level']})")
            if fusion_result['is_deceptive']:
                print(f"     Deceptive cues active!")
            
            # ---- CLEANUP: Remove temporary segment audio file ----
            try:
                if seg_audio and os.path.exists(seg_audio):
                    os.remove(seg_audio)
            except Exception as e:
                print(f"  Warning: Could not delete segment file {seg_audio}: {e}")

        # ------------------------------------------------------------------
        # 6. Overall summary & report
        # ------------------------------------------------------------------
        if not segment_results:
            print("No valid segments analyzed.")
            return None

        overall_score = np.mean([s['fusion']['final_deception_score'] for s in segment_results])
        deceptive_segments = sum(1 for s in segment_results if s['fusion']['is_deceptive'])
        total_segs = len(segment_results)

        # ------------------------------------------------------------------
        # 6. Generate Session Timeline (Deception score per second)
        # ------------------------------------------------------------------
        print("\nGenerating session-wide timeline data...")
        full_timeline = []
        for sec in range(int(video_duration_sec) + 1):
            # Check if this second falls within any analyzed segment
            matching_seg = next((s for s in segment_results if s['start_sec'] <= sec <= s['end_sec']), None)
            if matching_seg:
                score = matching_seg['fusion']['final_deception_score']
            else:
                # Default baseline score for non-suspect segments
                score = self.baseline_metrics.get('voice_stress', 25)
            
            full_timeline.append({
                "second": sec,
                "timestamp": f"{int(sec//60):02d}:{int(sec%60):02d}",
                "deception_score": round(float(score), 1)
            })

        report = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'video_path': video_path,
            'audio_path': audio_path,
            'question_context': question_context,
            'overall_deception_score': round(overall_score, 1),
            'deceptive_segments': deceptive_segments,
            'total_segments': total_segs,
            'timeline': full_timeline,
            'segments': segment_results,
            'conclusion': (
                f"Across {total_segs} analyzed responses, the average deception score was {overall_score:.1f}%. "
                f"{deceptive_segments} segment(s) flagged as deceptive."
            )
        }

        # Save JSON report
        os.makedirs(self.report_dir, exist_ok=True)
        report_path = os.path.join(self.report_dir, f"deception_report_{session_id}.json")
        
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.bool_,)):
                    return bool(obj)
                if isinstance(obj, (np.integer,)):
                    return int(obj)
                if isinstance(obj, (np.floating,)):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

        print("\n" + "=" * 60)
        print("   PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Annotated videos saved to: {self.video_dir}/")
        print(f"Combined presentation video with audio: {self.video_dir}/{stem}_combined_presentation.mp4")
        print(f"Processed {total_segs} suspect responses.")
        print(f"Average deception score: {overall_score:.1f}%")
        print(f"Deceptive segments: {deceptive_segments}/{total_segs}")
        print(f"Report saved to: {report_path}")
        print("-" * 60)
        if segment_results:
            print("  Q&A SUMMARY:")
            for s in segment_results:
                q = s.get('question', {}) or {}
                q_text = q.get('text', '') if q else ''
                a_text = s.get('transcript_original', '')[:80]
                if q_text:
                    print(f"  Q: \"{q_text[:80]}{'...' if len(q_text) > 80 else ''}\"")
                print(f"  A: \"{a_text}{'...' if len(s.get('transcript_original','')) > 80 else ''}\"")
                print(f"  → Score: {s['fusion']['final_deception_score']:.1f}% | "
                      f"{'DECEPTIVE' if s['fusion']['is_deceptive'] else 'TRUTHFUL'}")
                print()
        print("=" * 60)

        return report_path

    # ------------------------------------------------------------------
    #   Generate annotated full videos (including emotion)
    # ------------------------------------------------------------------
    def _generate_annotated_videos(self, video_path: str, stem: str):
        """Run each visual module on the full video in PARALLEL and save annotated copies at 720p."""
        # Calculate scale for 720p target height
        cap = cv2.VideoCapture(video_path)
        orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        scale = min(720.0 / orig_height, 1.0) if orig_height > 0 else 1.0
        if scale < 1.0:
            print(f"\nScaling output to 720p (scale={scale:.3f})...")

        print("\nGenerating annotated full videos (Parallel Process)...")
        modules = {
            'eye_gaze': self.eye_analyzer,
            'lip_jaw': self.lip_analyzer,
            'head_pose': self.head_analyzer,
            'asymmetry': self.asymmetry_analyzer,
            'hand_face': self.hand_analyzer,
            'emotion': self.emotion_analyzer
        }
        
        with ThreadPoolExecutor(max_workers=len(modules)) as executor:
            futures = []
            for name, analyzer in modules.items():
                out_path = os.path.join(self.video_dir, f"{stem}_{name}.mp4")
                print(f"  Scheduling {name} ...")
                futures.append(executor.submit(analyzer.process_video, video_path, output_path=out_path, verbose=False, scale=scale))
            
            # Wait for all to finish
            for f in futures:
                try: f.result()
                except Exception as e: print(f"  Module video generation failed: {e}")

        print("Annotated videos complete.\n")

    # ------------------------------------------------------------------
    #   Create 2x2 combined presentation video with audio
    # ------------------------------------------------------------------
    def _create_combined_video(self, stem: str, audio_path: str):
        """Stack eye_gaze, emotion, hand_face, lip_jaw in 2x2 grid,
        add original audio, and save as 'stem_combined_presentation.mp4'.
        """
        print("\nCreating 2x2 combined presentation video with audio...")
        # Filenames of the four selected modules
        eye_file = os.path.join(self.video_dir, f"{stem}_eye_gaze.mp4")
        emotion_file = os.path.join(self.video_dir, f"{stem}_emotion.mp4")
        hand_file = os.path.join(self.video_dir, f"{stem}_hand_face.mp4")
        lip_file = os.path.join(self.video_dir, f"{stem}_lip_jaw.mp4")

        # Ensure all four exist; if any missing, skip
        for f in [eye_file, emotion_file, hand_file, lip_file]:
            if not os.path.exists(f):
                print(f"  Warning: {f} not found, skipping combined video.")
                return

        combined_video = os.path.join(self.video_dir, f"{stem}_combined_presentation.mp4")
        
        # ffmpeg xstack 2x2: top-left, top-right, bottom-left, bottom-right
        cmd = [
            "ffmpeg", "-y",
            "-i", eye_file, "-i", emotion_file, "-i", hand_file, "-i", lip_file,
            "-i", audio_path,
            "-filter_complex",
            "[0:v][1:v][2:v][3:v]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[v]",
            "-map", "[v]", "-map", "4:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            combined_video
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"  Combined video saved: {combined_video}")
        except subprocess.CalledProcessError as e:
            print(f"  ffmpeg error: {e.stderr}")

    # ------------------------------------------------------------------
    #   Audio extraction
    # ------------------------------------------------------------------
    def _extract_audio(self, video_path: str) -> Optional[str]:
        """Extract audio stream from video using ffmpeg."""
        audio_path = tempfile.mktemp(suffix=".wav")
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            audio_path
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return audio_path
        except subprocess.CalledProcessError as e:
            print(f"ffmpeg error: {e.stderr}")
            return None

    def _analyze_baseline(self, video_path: str, audio_path: str, end_frame: int) -> Dict:
        """Analyzes the first few seconds of video/audio to establish 'normal' behavior."""
        # Eye baseline
        eye_data = self.eye_analyzer.process_video(video_path, end_frame=end_frame, verbose=False)
        # We'll use gaze stability (CENTER ratio) as the eye baseline score
        eye_base = (len([f for f in eye_data if f.get('gaze') == 'CENTER']) / len(eye_data) * 100) if eye_data else 80
        
        # Voice baseline
        voice_results = self.voice_analyzer.analyze_segment(audio_path, 0, end_frame/30.0, suppress_terminal=True)
        # Use overall deception score or default to 30
        voice_base = 30
        if voice_results and 'deception_analysis' in voice_results:
            voice_base = voice_results['deception_analysis'].get('overall_deception_score', 30)
        
        # Emotion baseline
        emo_data = self.emotion_analyzer.process_video(video_path, end_frame=end_frame, verbose=False)
        # Use 'emotion' key instead of 'dominant_emotion'
        from collections import Counter
        dom_emo = Counter([f['emotion'] for f in emo_data]).most_common(1)[0][0] if emo_data else "Neutral"

        return {
            'eye_gaze_score': eye_base,
            'voice_stress': voice_base,
            'dominant_emotion': dom_emo,
            'blink_rate': len([f for f in eye_data if f.get('blink_count', 0) > 0]) / (end_frame/30.0) if (end_frame > 0) else 0.5
        }

    def _detect_conflicts(self, face_cues: Dict, voice_stress: Dict) -> List[str]:
        """Detects contradictions between different modules (e.g. happy face + high stress voice)."""
        conflicts = []
        
        # 1. Emotional Mismatch
        dominant_emotion = face_cues.get('emotion', {}).get('dominant_emotion', 'Neutral')
        stress_score = voice_stress.get('overall_deception_score', 0)
        
        if dominant_emotion in ['Happy', 'Neutral'] and stress_score > 60:
            conflicts.append("Emotional Conflict: Subject appears calm but voice indicates high psychological stress.")
            
        # 2. Gaze vs Voice
        gaze_stab = face_cues.get('eye_gaze', {}).get('gaze_stability', 100)
        if gaze_stab < 40 and stress_score < 30:
            conflicts.append("Behavioral Conflict: High gaze instability with unusually calm voice (potential calculated lying).")
            
        return conflicts

    def _detect_spikes(self, current_data: Dict, baseline: Dict) -> List[str]:
        """Detects sudden spikes in behavior compared to the baseline."""
        spikes = []
        if not baseline: return spikes
        
        # Voice Spike
        curr_voice = current_data.get('voice_stress', {}).get('overall_deception_score', 0)
        base_voice = baseline.get('voice_stress', 30)
        if curr_voice > (base_voice + 25):
            spikes.append(f"Voice Stress Spike: +{curr_voice - base_voice:.1f}% increase from normal baseline.")
            
        # Gaze Spike
        curr_gaze = current_data.get('face_cues', {}).get('eye_gaze', {}).get('gaze_stability', 100)
        base_gaze = baseline.get('eye_gaze_score', 50)
        if curr_gaze < (base_gaze - 30):
            spikes.append("Gaze Stability Spike: Sudden drop in eye focus compared to baseline.")
            
        return spikes


# ---------------------------------------------------------------------
#   Command‑line entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deceptron Deception Detection Pipeline")
    parser.add_argument("video", help="Path to interrogation video file")
    parser.add_argument("--audio", help="Optional extracted audio file (.wav)")
    parser.add_argument("--report_dir", default="reports", help="Directory for report JSON files")
    parser.add_argument("--video_dir", default="results", help="Directory for annotated output videos")
    parser.add_argument("--question", default="", help="Interview question (for better NLP context)")
    args = parser.parse_args()

    pipeline = DeceptionPipeline(report_dir=args.report_dir, video_dir=args.video_dir)
    report_path = pipeline.process(args.video, args.audio, question_context=args.question)
    if report_path:
        print(f"Final report: {report_path}")
    else:
        print("Pipeline failed.")