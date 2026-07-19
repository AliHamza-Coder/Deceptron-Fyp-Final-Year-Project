import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import os

class HeadPoseAnalyzer:
    """Analyses head pose: angles, depth, stiffness, withdrawal, nodding/shaking."""

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.IDX_NOSE = 1
        self.IDX_CHIN = 152
        self.IDX_LEYE = 33
        self.IDX_REYE = 263
        self.IDX_LMOUTH = 61
        self.IDX_RMOUTH = 291

        self.model_points = np.array([
            [0.0, 0.0, 0.0],
            [0.0, -65.0, -30.0],
            [-35.0, 30.0, -35.0],
            [35.0, 30.0, -35.0],
            [-30.0, -45.0, -40.0],
            [30.0, -45.0, -40.0]
        ], dtype=np.float32)

        self.stiffness_window_sec = 1.0
        self.nodding_window_sec = 1.0
        self.nodding_zero_cross_thresh = 3
        self.nodding_amplitude_thresh = 3.0
        self.withdrawal_scale = 500.0
        self.stiffness_scale = 50.0

        self.baseline_depth = None
        self.baseline_pitch = None
        self.baseline_yaw = None
        self.baseline_roll = None

    def _landmark_point(self, landmarks, idx, img_w, img_h):
        lm = landmarks[idx]
        return (int(lm.x * img_w), int(lm.y * img_h))

    def _build_image_points(self, landmarks, img_w, img_h):
        return np.array([
            self._landmark_point(landmarks, self.IDX_NOSE, img_w, img_h),
            self._landmark_point(landmarks, self.IDX_CHIN, img_w, img_h),
            self._landmark_point(landmarks, self.IDX_LEYE, img_w, img_h),
            self._landmark_point(landmarks, self.IDX_REYE, img_w, img_h),
            self._landmark_point(landmarks, self.IDX_LMOUTH, img_w, img_h),
            self._landmark_point(landmarks, self.IDX_RMOUTH, img_w, img_h)
        ], dtype=np.float32)

    def _rotation_matrix_to_euler_angles(self, R):
        sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
        if sy > 1e-6:
            pitch = np.arctan2(R[2, 1], R[2, 2])
            yaw = np.arctan2(-R[2, 0], sy)
            roll = np.arctan2(R[1, 0], R[0, 0])
        else:
            pitch = np.arctan2(-R[1, 2], R[1, 1]); yaw = np.arctan2(-R[2, 0], sy); roll = 0.0
        return float(np.rad2deg(pitch)), float(np.rad2deg(yaw)), float(np.rad2deg(roll))

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
        cam_matrix = np.array([[width, 0, width/2], [0, width, height/2], [0, 0, 1]], dtype=np.float32)
        dist_coeffs = np.zeros((4, 1))

        auto_calib = (start_frame == 1 and self.baseline_depth is None)
        calib_duration, calib_ended = 5.0, not auto_calib
        calib_depths, calib_pitches, calib_yaws, calib_rolls = [], [], [], []

        stiff_len = max(2, int(fps * self.stiffness_window_sec))
        p_win, y_win, r_win = deque(maxlen=stiff_len), deque(maxlen=stiff_len), deque(maxlen=stiff_len)
        nod_len = max(2, int(fps * self.nodding_window_sec))
        pv_hist, yv_hist, pval_hist, yval_hist = deque(maxlen=nod_len), deque(maxlen=nod_len), deque(maxlen=nod_len), deque(maxlen=nod_len)

        frame_data_list, frame_idx = [], 0
        prev_p = prev_y = None

        while True:
            ret, frame = cap.read()
            if not ret: break
            frame_idx += 1
            if frame_idx < start_frame: continue
            if frame_idx > end_frame: break

            timestamp = frame_idx / fps
            pitch = yaw = roll = withdrawal = stiffness = 0.0
            z_depth = 500.0
            is_nodding = is_shaking = False

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                img_pts = self._build_image_points(landmarks, width, height)
                nose_img = tuple(img_pts[0].astype(int))

                success, rvec, tvec = cv2.solvePnP(self.model_points, img_pts, cam_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
                if success:
                    R, _ = cv2.Rodrigues(rvec)
                    pitch, yaw, roll = self._rotation_matrix_to_euler_angles(R)
                    z_depth = float(np.linalg.norm(tvec))

                    if auto_calib and not calib_ended and timestamp <= calib_duration:
                        calib_depths.append(z_depth); calib_pitches.append(pitch); calib_yaws.append(yaw); calib_rolls.append(roll)
                        if out: cv2.putText(frame, "Scanning Signal...", (10, 30), 0, 0.8, (0, 255, 255), 2); out.write(cv2.resize(frame, (out_w, out_h)) if scale != 1.0 else frame)
                        frame_data_list.append({'frame_num': frame_idx, 'timestamp': timestamp, 'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0, 'z_depth': 0.0, 'stiffness_score': 0.0, 'withdrawal_score': 0.0, 'is_nodding': False, 'is_shaking': False})
                        continue

                    if auto_calib and not calib_ended:
                        calib_ended = True
                        self.baseline_depth = float(np.mean(calib_depths)) if calib_depths else z_depth
                        self.baseline_pitch = float(np.mean(calib_pitches)) if calib_pitches else pitch
                        self.baseline_yaw = float(np.mean(calib_yaws)) if calib_yaws else yaw
                        self.baseline_roll = float(np.mean(calib_rolls)) if calib_rolls else roll

                    if self.baseline_depth:
                        withdrawal = max(0.0, min(100.0, ((z_depth - self.baseline_depth) / self.baseline_depth) * self.withdrawal_scale))

                    p_win.append(pitch); y_win.append(yaw); r_win.append(roll)
                    if len(p_win) >= 2: stiffness = max(0.0, min(100.0, 100.0 - self.stiffness_scale * np.mean([np.std(p_win), np.std(y_win), np.std(r_win)])))

                    pv = pitch - prev_p if prev_p is not None else 0.0
                    yv = yaw - prev_y if prev_y is not None else 0.0
                    prev_p, prev_y = pitch, yaw
                    pv_hist.append(pv); yv_hist.append(yv); pval_hist.append(pitch); yval_hist.append(yaw)

                    if len(pv_hist) >= 3:
                        is_nodding = sum(1 for i in range(1, len(pv_hist)) if np.sign(pv_hist[i-1]) != np.sign(pv_hist[i]) and pv_hist[i] != 0) >= self.nodding_zero_cross_thresh and (max(pval_hist) - min(pval_hist)) >= self.nodding_amplitude_thresh
                        is_shaking = sum(1 for i in range(1, len(yv_hist)) if np.sign(yv_hist[i-1]) != np.sign(yv_hist[i]) and yv_hist[i] != 0) >= self.nodding_zero_cross_thresh and (max(yval_hist) - min(yval_hist)) >= self.nodding_amplitude_thresh

                    if out:
                        axis_pts, _ = cv2.projectPoints(np.array([[50,0,0],[0,50,0],[0,0,50]], dtype=np.float32), rvec, tvec, cam_matrix, dist_coeffs)
                        cv2.line(frame, nose_img, tuple(axis_pts[0][0].astype(int)), (0,0,255), 2)
                        cv2.line(frame, nose_img, tuple(axis_pts[1][0].astype(int)), (0,255,0), 2)
                        cv2.line(frame, nose_img, tuple(axis_pts[2][0].astype(int)), (255,0,0), 2)
                        stext = f"P:{pitch:.1f} Y:{yaw:.1f} R:{roll:.1f} Stiff:{stiffness:.0f}%"
                        cv2.putText(frame, stext, (10, 20), 0, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

            if out: out.write(cv2.resize(frame, (out_w, out_h)) if scale != 1.0 else frame)
            frame_data_list.append({'frame_num': frame_idx, 'timestamp': timestamp, 'pitch': round(float(pitch), 2), 'yaw': round(float(yaw), 2), 'roll': round(float(roll), 2), 'z_depth': round(float(z_depth), 2), 'stiffness_score': round(float(stiffness), 2), 'withdrawal_score': round(float(withdrawal), 2), 'is_nodding': bool(is_nodding), 'is_shaking': bool(is_shaking)})

        cap.release()
        if out: out.release()
        return frame_data_list

    def get_summary(self, data):
        if not data: return {}
        eval_data = [d for d in data if d['pitch'] != 0 or d['yaw'] != 0]
        if not eval_data: return {"total_frames": len(data), "frames": data}
        return {
            "total_frames": len(data),
            "averages": {
                "pitch": round(float(np.mean([d['pitch'] for d in eval_data])), 2),
                "yaw": round(float(np.mean([d['yaw'] for d in eval_data])), 2),
                "roll": round(float(np.mean([d['roll'] for d in eval_data])), 2),
                "stiffness": round(float(np.mean([d['stiffness_score'] for d in eval_data])), 1),
                "withdrawal": round(float(np.mean([d['withdrawal_score'] for d in eval_data])), 1)
            },
            "dynamics": {
                "nodding_percent": round((sum(1 for d in eval_data if d['is_nodding']) / len(eval_data)) * 100, 1),
                "shaking_percent": round((sum(1 for d in eval_data if d['is_shaking']) / len(eval_data)) * 100, 1)
            },
            "frames": data
        }

    def _print_report(self, data):
        s = self.get_summary(data)
        print(f"\n[POSE REPORT] Frames: {s['total_frames']}")

if __name__ == "__main__":
    path = input("Video Path: ").strip().strip('"')
    if os.path.exists(path):
        analyzer = HeadPoseAnalyzer()
        res = analyzer.process_video(path, output_path="pose_output.mp4")
        analyzer._print_report(res)