import cv2
import mediapipe as mp
import numpy as np
import os

class EyeGazeAnalyzer:
    """Analyzes eye gaze and blink detection with high accuracy and detailed reporting."""

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        self.L_EYE_TOP, self.L_EYE_BOT = 386, 374
        self.L_EYE_LEFT, self.L_EYE_RIGHT = 362, 263
        self.R_EYE_TOP, self.R_EYE_BOT = 159, 145
        self.R_EYE_LEFT, self.R_EYE_RIGHT = 33, 133
        
        self.EAR_THRESHOLD = 0.22
        self.BLINK_FRAME_CONSEC = 2
        self.blink_counter = 0
        self.total_blinks = 0
        self.blink_timestamps = []

    def get_ear(self, eye_pts):
        v1 = np.linalg.norm(eye_pts[12] - eye_pts[4])
        v2 = np.linalg.norm(eye_pts[14] - eye_pts[2])
        h = np.linalg.norm(eye_pts[0] - eye_pts[8])
        return (v1 + v2) / (2.0 * h)

    def process_video(self, input_path, output_path=None, start_frame=None, end_frame=None, verbose=True, scale=1.0):
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out_w, out_h = int(width * scale), int(height * scale)
        total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if start_frame is None: start_frame = 1
        if end_frame is None: end_frame = total_f
        
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v'); out = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))
        frame_data, frame_idx = [], 0
        self.total_blinks = 0; self.blink_timestamps = []

        while True:
            ret, frame = cap.read()
            if not ret: break
            frame_idx += 1
            if frame_idx < start_frame: continue
            if frame_idx > end_frame: break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = self.face_mesh.process(rgb)
            ear, gaze = 0.0, "CENTER"

            if res.multi_face_landmarks:
                mesh = res.multi_face_landmarks[0].landmark
                l_pts = np.array([(mesh[p].x * width, mesh[p].y * height) for p in self.LEFT_EYE])
                r_pts = np.array([(mesh[p].x * width, mesh[p].y * height) for p in self.RIGHT_EYE])
                ear = (self.get_ear(l_pts) + self.get_ear(r_pts)) / 2.0
                
                if ear < self.EAR_THRESHOLD:
                    self.blink_counter += 1
                else:
                    if self.blink_counter >= self.BLINK_FRAME_CONSEC:
                        self.total_blinks += 1
                        self.blink_timestamps.append(round(frame_idx / fps, 2))
                    self.blink_counter = 0
                
                l_iris = np.mean([(mesh[p].x * width, mesh[p].y * height) for p in self.LEFT_IRIS], axis=0)
                l_left = np.array((mesh[self.L_EYE_LEFT].x * width, mesh[self.L_EYE_LEFT].y * height))
                l_right = np.array((mesh[self.L_EYE_RIGHT].x * width, mesh[self.L_EYE_RIGHT].y * height))
                
                total_w = np.linalg.norm(l_left - l_right)
                if total_w > 0:
                    ratio = np.linalg.norm(l_iris - l_left) / total_w
                    if ratio < 0.4: gaze = "LEFT"
                    elif ratio > 0.6: gaze = "RIGHT"
                
                if out:
                    for p in self.LEFT_EYE + self.RIGHT_EYE: cv2.circle(frame, (int(mesh[p].x*width), int(mesh[p].y*height)), 1, (0,255,0), -1)
                    cv2.putText(frame, f"EAR: {ear:.2f} Blinks: {self.total_blinks} Gaze: {gaze}", (10,30), 0, 0.7, (0,0,255), 2)

            if out: out.write(cv2.resize(frame, (out_w, out_h)) if scale != 1.0 else frame)
            frame_data.append({'frame_num': frame_idx, 'timestamp': frame_idx/fps, 'ear': round(ear, 3), 'gaze': gaze, 'blink_count': self.total_blinks})
            if verbose and frame_idx % 30 == 0: print(f"Gaze Processed: {frame_idx}/{end_frame}")

        cap.release()
        if out: out.release()
        return frame_data

    def get_summary(self, data):
        if not data: return {}
        gazes = [d['gaze'] for d in data]
        dist = {g: round(gazes.count(g)/len(gazes)*100, 1) for g in set(gazes)}
        
        # Timeline of Gaze
        timeline = []
        if data:
            start_f = data[0]['frame_num']
            curr_g = data[0]['gaze']
            for i in range(1, len(data)):
                if data[i]['gaze'] != curr_g:
                    timeline.append({"start_frame": start_f, "end_frame": data[i-1]['frame_num'], "gaze": curr_g})
                    start_f = data[i]['frame_num']; curr_g = data[i]['gaze']
            timeline.append({"start_frame": start_f, "end_frame": data[-1]['frame_num'], "gaze": curr_g})

        return {
            "total_frames": len(data),
            "blinks": {"total": self.total_blinks, "timestamps": self.blink_timestamps, "rate_per_min": round(self.total_blinks / (len(data)/30) * 60, 1) if data else 0},
            "distribution": dist,
            "averages": {"ear": round(np.mean([d['ear'] for d in data]), 3)},
            "timeline": timeline,
            "frames": data  # Export every single frame's raw data
        }

    def _print_report(self, data):
        s = self.get_summary(data)
        print(f"\n[GAZE REPORT] Blinks: {s['blinks']['total']} | Avg EAR: {s['averages']['ear']}")