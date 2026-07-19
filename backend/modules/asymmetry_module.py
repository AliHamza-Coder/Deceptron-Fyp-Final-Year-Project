import cv2
import mediapipe as mp
import numpy as np
from collections import defaultdict
import os

class AsymmetryAnalyzer:
    """Detects facial asymmetry relative to a personal baseline."""

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.NOSE_BRIDGE = 6
        self.CHIN = 152
        self.MOUTH_LEFT = 61
        self.MOUTH_RIGHT = 291
        self.BROW_LEFT = 105
        self.BROW_RIGHT = 334
        self.EYE_LEFT = 33
        self.EYE_RIGHT = 263

        self.asymmetry_threshold = 15.0
        self.alert_threshold = 30.0

        self.baseline_mouth = None
        self.baseline_brow = None
        self.baseline_eye = None

    def _distance(self, pt1, pt2):
        return np.linalg.norm(np.array(pt1) - np.array(pt2))

    def _landmark_point(self, landmarks, idx, img_w, img_h):
        lm = landmarks[idx]
        return (int(lm.x * img_w), int(lm.y * img_h))

    def _raw_asymmetry(self, landmarks, center_idx, left_idx, right_idx, img_w, img_h):
        center = self._landmark_point(landmarks, center_idx, img_w, img_h)
        left = self._landmark_point(landmarks, left_idx, img_w, img_h)
        right = self._landmark_point(landmarks, right_idx, img_w, img_h)
        dist_left = self._distance(center, left)
        dist_right = self._distance(center, right)
        avg_dist = (dist_left + dist_right) / 2.0
        if avg_dist < 1e-6: return 0.0
        return min((abs(dist_left - dist_right) / avg_dist) * 100.0, 100.0)

    def process_video(self, input_path, output_path=None, start_frame=None, end_frame=None, verbose=True, scale=1.0):
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened(): raise ValueError(f"Cannot open video: {input_path}")
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out_w, out_h = int(width * scale), int(height * scale)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if start_frame is None: start_frame = 1
        if end_frame is None: end_frame = total_frames

        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'H264'); out = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))

        auto_calib = (start_frame == 1 and self.baseline_mouth is None)
        calib_duration, calib_ended = 5.0, not auto_calib
        calib_mouth, calib_brow, calib_eye = [], [], []

        frame_data_list, frame_idx = [], 0

        while True:
            ret, frame = cap.read()
            if not ret: break
            frame_idx += 1
            if frame_idx < start_frame: continue
            if frame_idx > end_frame: break

            timestamp = frame_idx / fps
            mouth_dev = brow_dev = eye_dev = total_dev = 0.0
            status = 'SYMMETRIC'

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if results.multi_face_landmarks:
                lms = results.multi_face_landmarks[0].landmark
                rm = self._raw_asymmetry(lms, self.NOSE_BRIDGE, self.MOUTH_LEFT, self.MOUTH_RIGHT, width, height)
                rb = self._raw_asymmetry(lms, self.NOSE_BRIDGE, self.BROW_LEFT, self.BROW_RIGHT, width, height)
                re = self._raw_asymmetry(lms, self.NOSE_BRIDGE, self.EYE_LEFT, self.EYE_RIGHT, width, height)

                if auto_calib and not calib_ended and timestamp <= calib_duration:
                    calib_mouth.append(rm); calib_brow.append(rb); calib_eye.append(re)
                    if out: cv2.putText(frame, "Scanning Signal...", (10, 30), 0, 0.8, (0, 255, 255), 2); out.write(cv2.resize(frame, (out_w, out_h)) if scale != 1.0 else frame)
                    frame_data_list.append({'frame_num': frame_idx, 'timestamp': timestamp, 'mouth_asym': 0.0, 'brow_asym': 0.0, 'eye_asym': 0.0, 'total_asym': 0.0, 'status': 'SYMMETRIC'})
                    continue

                if auto_calib and not calib_ended:
                    calib_ended = True
                    self.baseline_mouth, self.baseline_brow, self.baseline_eye = np.mean(calib_mouth), np.mean(calib_brow), np.mean(calib_eye)

                if self.baseline_mouth is not None:
                    mouth_dev, brow_dev, eye_dev = max(0.0, rm - self.baseline_mouth), max(0.0, rb - self.baseline_brow), max(0.0, re - self.baseline_eye)
                    total_dev = (mouth_dev + brow_dev + eye_dev) / 3.0
                    status = 'ASYMMETRIC' if total_dev >= self.asymmetry_threshold else 'SYMMETRIC'

                if out:
                    nose_br = self._landmark_point(lms, self.NOSE_BRIDGE, width, height)
                    chin = self._landmark_point(lms, self.CHIN, width, height)
                    cv2.line(frame, nose_br, chin, (0, 255, 0), 2)
                    text = f"M:{mouth_dev:.1f}% B:{brow_dev:.1f}% E:{eye_dev:.1f}% | Total:{total_dev:.1f}% | {status}"
                    bg = (0, 0, 255) if total_dev > self.alert_threshold else (0, 255, 255) if status == 'ASYMMETRIC' else (0, 255, 0)
                    (tw, th), _ = cv2.getTextSize(text, 0, 0.45, 1)
                    cv2.rectangle(frame, (5, 5), (5 + tw + 10, 5 + th + 10), bg, -1)
                    cv2.putText(frame, text, (10, 20), 0, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
                    if total_dev > self.alert_threshold: cv2.putText(frame, ">>> ASYMMETRIC EXPRESSION", (10, height - 10), 0, 0.7, (0, 0, 255), 2)

            if out: out.write(cv2.resize(frame, (out_w, out_h)) if scale != 1.0 else frame)
            frame_data_list.append({'frame_num': frame_idx, 'timestamp': timestamp, 'mouth_asym': round(mouth_dev, 2), 'brow_asym': round(brow_dev, 2), 'eye_asym': round(eye_dev, 2), 'total_asym': round(total_dev, 2), 'status': status})
            if verbose and frame_idx % 30 == 0: print(f"Asym Processed: {frame_idx}/{end_frame}")

        cap.release()
        if out: out.release()
        return frame_data_list

    def get_summary(self, data):
        if not data: return {}
        eval_data = [d for d in data if d['mouth_asym'] > 0 or d['brow_asym'] > 0]
        if not eval_data: return {"total_frames": len(data)}
        return {
            "total_frames": len(data),
            "averages": {
                "mouth_asym": round(np.mean([d['mouth_asym'] for d in eval_data]), 2),
                "brow_asym": round(np.mean([d['brow_asym'] for d in eval_data]), 2),
                "eye_asym": round(np.mean([d['eye_asym'] for d in eval_data]), 2),
                "total_asym": round(np.mean([d['total_asym'] for d in eval_data]), 2)
            },
            "asymmetric_percent": round((sum(1 for d in eval_data if d['status'] == 'ASYMMETRIC') / len(eval_data)) * 100, 1) if eval_data else 0,
            "frames": data  # Raw frame-by-frame data
        }

    def _print_report(self, data):
        s = self.get_summary(data)
        print(f"\nASYM REPORT: {s['total_frames']} frames")
        if 'averages' in s: print(f"  Avg Asym: {s['averages']['total_asym']}%")

if __name__ == "__main__":
    path = input("Video Path: ").strip().strip('"')
    if os.path.exists(path):
        analyzer = AsymmetryAnalyzer()
        res = analyzer.process_video(path, output_path="asym_output.mp4")
        analyzer._print_report(res)