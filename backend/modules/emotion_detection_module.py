"""
emotion_detection_module.py

Real‑time emotion detection using HSEmotion + MediaPipe Face Detection.
Standalone: python emotion_detection_module.py → asks for video, prints per‑frame
analysis, saves annotated video, and prints a final timeline report.

Pipeline‑ready: supports start/end frame & optional output video.

Dependencies: hsemotion, torch, mediapipe, opencv, numpy
"""

import cv2
import mediapipe as mp
import torch
import numpy as np
from collections import defaultdict
import os
from hsemotion.facial_emotions import HSEmotionRecognizer


class EmotionAnalyzer:
    """Per‑frame emotion classification using HSEmotion + MediaPipe Face Detection."""

    def __init__(self, model_name='enet_b0_8_best_vgaf', device=None):
        # Use Face Detection for accurate bounding boxes
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5)

        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Loading Emotion Detection Model ({model_name}) on {device}...")
        try:
            self.fer = HSEmotionRecognizer(model_name=model_name, device=device)
        except Exception as e:
            if "WeightsUnpickler" in str(e) or "unpickle" in str(e):
                print("Patching torch.load for compatibility...")
                original_load = torch.load
                torch.load = lambda *args, **kwargs: original_load(*args, **{**kwargs, 'weights_only': False})
                self.fer = HSEmotionRecognizer(model_name=model_name, device=device)
                torch.load = original_load
            else:
                raise e
        print("Model loaded successfully.")

    def process_video(self, input_path, output_path=None,
                      start_frame=None, end_frame=None,
                      verbose=True, scale=1.0):
        """Analyze video, optionally save annotated copy, return per‑frame list.

        Args:
            input_path: path to video file
            output_path: if not None, annotated video is saved here
            start_frame: first frame (1‑based)
            end_frame: last frame (inclusive)
            verbose: print per‑frame progress
            scale: output resolution scale factor (1.0 = full, 0.667 = 720p for 1080p source)

        Returns:
            list of dicts: [{'frame_num', 'timestamp', 'emotion', 'confidence'}, …]
        """
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {input_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out_w, out_h = int(width * scale), int(height * scale)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if start_frame is None:
            start_frame = 1
        if end_frame is None:
            end_frame = total_frames
        start_frame = max(1, start_frame)
        end_frame = min(total_frames, end_frame)

        out = None
        if output_path is not None:
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            out = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))
        frame_data = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_idx += 1
            if frame_idx < start_frame:
                continue
            if frame_idx > end_frame:
                break

            timestamp = frame_idx / fps
            emotion = 'Neutral'
            confidence = 0.0

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb)

            if results.detections:
                detection = results.detections[0]
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * width)
                y = int(bbox.ymin * height)
                w = int(bbox.width * width)
                h = int(bbox.height * height)

                x1 = max(0, x)
                y1 = max(0, y)
                x2 = min(width, x + w)
                y2 = min(height, y + h)

                face_crop = frame[y1:y2, x1:x2]
                if face_crop.size != 0:
                    try:
                        # HSEmotion returns (label, scores) where scores is array-like
                        emotion, scores = self.fer.predict_emotions(face_crop, logits=False)
                        # confidence = highest score * 100
                        confidence = float(max(scores)) * 100
                    except Exception as e:
                        if verbose:
                            print(f"Frame {frame_idx:04d}: prediction error - {e}")
                        emotion = 'Neutral'
                        confidence = 0.0

                # Draw overlays (only for output video)
                if out is not None:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{emotion} ({confidence:.1f}%)"
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Terminal output
            if verbose:
                print(f"Frame {frame_idx:04d}: {emotion} ({confidence:.1f}%)")

            frame_data.append({
                'frame_num': frame_idx,
                'timestamp': timestamp,
                'emotion': emotion,
                'confidence': round(confidence, 2)
            })

            if out is not None:
                out.write(cv2.resize(frame, (out_w, out_h)) if scale != 1.0 else frame)

        cap.release()
        if out is not None:
            out.release()
        # Do NOT close face_detection – allow pipeline reuse

        return frame_data

    def get_summary(self, frame_data):
        """Calculate distribution and timeline for API reporting."""
        if not frame_data:
            return {}

        # 1. Distribution
        emotions = [f['emotion'] for f in frame_data]
        counts = defaultdict(int)
        for e in emotions:
            counts[e] += 1
        
        distribution = {}
        for e, c in counts.items():
            distribution[e] = {
                "count": c,
                "percentage": round((c / len(frame_data)) * 100, 1)
            }

        # 2. Timeline
        timeline = []
        if emotions:
            seq_start = frame_data[0]['frame_num']
            seq_emo = emotions[0]
            for i in range(1, len(emotions)):
                if emotions[i] != seq_emo:
                    end = frame_data[i-1]['frame_num']
                    timeline.append({
                        "start": seq_start,
                        "end": end,
                        "emotion": seq_emo,
                        "frames": end - seq_start + 1
                    })
                    seq_start = frame_data[i]['frame_num']
                    seq_emo = emotions[i]
            end = frame_data[-1]['frame_num']
            timeline.append({
                "start": seq_start,
                "end": end,
                "emotion": seq_emo,
                "frames": end - seq_start + 1
            })

        return {
            "total_frames": len(frame_data),
            "distribution": distribution,
            "timeline": timeline,
            "frames": frame_data
        }

    def _print_report(self, data):
        """Print final statistics (standalone mode)."""
        summary = self.get_summary(data)
        if not summary: return

        print("\n" + "=" * 50)
        print("         FINAL EMOTION ANALYSIS")
        print("=" * 50)
        print(f"Total Frames Processed: {summary['total_frames']}")
        print("-" * 50)
        print("EMOTION DISTRIBUTION:")
        for e, stats in sorted(summary['distribution'].items(), key=lambda x: -x[1]['count']):
            print(f"- {e:10s}: {stats['percentage']:5.1f}% ({stats['count']} frames)")
        print("-" * 50)
        print("EMOTION TIMELINE (Frame Sequences):")
        for seq in summary['timeline']:
            print(f"[{seq['start']:04d} to {seq['end']:04d}] : {seq['emotion']} (for {seq['frames']} frames)")
        print("=" * 50)


# -------------------------------------------------------------------------
#   Standalone execution
# -------------------------------------------------------------------------
if __name__ == "__main__":
    input_path = input("Enter the video file path: ").strip().strip('"').strip("'")
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        exit(1)

    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{stem}_emotion.mp4")

    print(f"Analyzing: {input_path}")
    analyzer = EmotionAnalyzer()
    data = analyzer.process_video(input_path, output_path, verbose=True)

    if data:
        analyzer._print_report(data)
        print(f"Output video saved to: {output_path}")
    else:
        print("No frames processed.")