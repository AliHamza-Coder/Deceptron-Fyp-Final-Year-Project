import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import os

class LipJawAnalyzer:
    """Analyzes lip compression, jaw tightness, and chin tremor with high accuracy."""

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.jaw_tightness_threshold = 50
        self.oral_stress_threshold = 50
        self.lip_seal_ratio_threshold = 0.01
        self.tremor_window = 5
        self.tremor_scale = 100.0

        self.NOSE_TIP = 4
        self.CHIN = 152
        self.INNER_LIP_TOP = 13
        self.INNER_LIP_BOTTOM = 14
        self.MOUTH_LEFT = 78
        self.MOUTH_RIGHT = 308
        self.LEFT_EYE_OUTER = 130
        self.RIGHT_EYE_OUTER = 359

        self.baseline_nose_chin = None
        self.baseline_lip_ratio = None
        self.baseline_face_scale = None

    def _distance(self, pt1, pt2):
        return np.linalg.norm(np.array(pt1) - np.array(pt2))

    def _landmark_point(self, landmarks, idx, img_w, img_h):
        lm = landmarks[idx]
        return (lm.x * img_w, lm.y * img_h)

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
            fourcc = cv2.VideoWriter_fourcc(*'mp4v'); out = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))
        auto_calib = (start_frame == 1 and self.baseline_nose_chin is None)
        calib_duration, calib_ended = 5.0, not auto_calib
        calib_nose_chin, calib_lip_ratios, calib_face_scale = [], [], []

        chin_positions = deque(maxlen=self.tremor_window)
        frame_data_list, frame_idx = [], 0

        while True:
            ret, frame = cap.read()
            if not ret: break
            frame_idx += 1
            if frame_idx < start_frame: continue
            if frame_idx > end_frame: break

            timestamp = frame_idx / fps
            jaw_tightness = oral_stress = chin_tremor = 0.0
            lip_status = jaw_status = 'NORMAL'
            lip_disappear = False

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                ntip = self._landmark_point(landmarks, self.NOSE_TIP, width, height)
                chin = self._landmark_point(landmarks, self.CHIN, width, height)
                ltop = self._landmark_point(landmarks, self.INNER_LIP_TOP, width, height)
                lbot = self._landmark_point(landmarks, self.INNER_LIP_BOTTOM, width, height)
                mleft = self._landmark_point(landmarks, self.MOUTH_LEFT, width, height)
                mright = self._landmark_point(landmarks, self.MOUTH_RIGHT, width, height)
                leye = self._landmark_point(landmarks, self.LEFT_EYE_OUTER, width, height)
                reye = self._landmark_point(landmarks, self.RIGHT_EYE_OUTER, width, height)

                ncdist = self._distance(ntip, chin)
                lheight = self._distance(ltop, lbot)
                mwidth = self._distance(mleft, mright)
                fscale = self._distance(leye, reye)
                lratio = lheight / mwidth if mwidth > 0 else 1.0

                if auto_calib and not calib_ended and timestamp <= calib_duration:
                    calib_nose_chin.append(ncdist); calib_face_scale.append(fscale)
                    if mwidth > 0: calib_lip_ratios.append(lratio)
                    if out: cv2.putText(frame, "Scanning Signal...", (10, 30), 0, 0.8, (0, 255, 255), 2); out.write(cv2.resize(frame, (out_w, out_h)) if scale != 1.0 else frame)
                    frame_data_list.append({'frame_num': frame_idx, 'timestamp': timestamp, 'jaw_tightness': 0.0, 'oral_stress': 0.0, 'lip_status': 'NORMAL', 'jaw_status': 'NORMAL', 'chin_tremor': 0.0, 'lip_disappear': False})
                    continue

                if auto_calib and not calib_ended:
                    calib_ended = True
                    self.baseline_nose_chin = float(np.mean(calib_nose_chin)) if calib_nose_chin else ncdist
                    self.baseline_face_scale = float(np.mean(calib_face_scale)) if calib_face_scale else fscale
                    self.baseline_lip_ratio = float(np.mean(calib_lip_ratios)) if calib_lip_ratios else lratio

                if self.baseline_nose_chin: jaw_tightness = max(0.0, min(100.0, (1.0 - (ncdist / self.baseline_nose_chin)) * 100.0))
                if self.baseline_lip_ratio and lratio < self.baseline_lip_ratio: 
                    oral_stress = max(0.0, min(100.0, (1.0 - (lratio / self.baseline_lip_ratio)) * 100.0))
                
                lip_disappear = (lratio < self.lip_seal_ratio_threshold)
                jaw_status = 'TENSED' if jaw_tightness >= self.jaw_tightness_threshold else 'NORMAL'
                lip_status = 'TENSED' if oral_stress >= self.oral_stress_threshold else 'NORMAL'

                norm_chin = (chin[0] / self.baseline_face_scale, chin[1] / self.baseline_face_scale) if self.baseline_face_scale else chin
                chin_positions.append(norm_chin)
                if len(chin_positions) >= 2:
                    positions = np.array(chin_positions)
                    mean_pos = np.mean(positions, axis=0)
                    std_dev = np.std(np.linalg.norm(positions - mean_pos, axis=1))
                    chin_tremor = max(0.0, min(100.0, std_dev * self.tremor_scale))

                if out:
                    cv2.line(frame, (int(ltop[0]), int(ltop[1])), (int(lbot[0]), int(lbot[1])), (0, 0, 255), 2)
                    cv2.line(frame, (int(mleft[0]), int(mleft[1])), (int(mright[0]), int(mright[1])), (0, 255, 255), 2)
                    cv2.line(frame, (int(ntip[0]), int(ntip[1])), (int(chin[0]), int(chin[1])), (0, 165, 255), 2)
                    
                    stext = f"Jaw: {jaw_tightness:.0f}% | Oral: {oral_stress:.0f}% | Jaw: {jaw_status} | Lip: {lip_status} | Tremor: {chin_tremor:.0f}%"
                    bg = (255, 105, 180) if lip_disappear else (0, 0, 255) if jaw_status == 'TENSED' or lip_status == 'TENSED' else (0, 255, 0)
                    (tw, th), _ = cv2.getTextSize(stext, 0, 0.45, 1)
                    cv2.rectangle(frame, (5, 5), (5 + tw + 10, 5 + th + 10), bg, -1)
                    cv2.putText(frame, stext, (10, 20), 0, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

            if out: out.write(cv2.resize(frame, (out_w, out_h)) if scale != 1.0 else frame)
            frame_data_list.append({
                'frame_num': frame_idx, 'timestamp': timestamp, 
                'jaw_tightness': round(float(jaw_tightness), 2), 'oral_stress': round(float(oral_stress), 2), 
                'lip_status': lip_status, 'jaw_status': jaw_status, 
                'chin_tremor': round(float(chin_tremor), 2), 'lip_disappear': bool(lip_disappear)
            })

        cap.release()
        if out: out.release()
        return frame_data_list

    def get_summary(self, data):
        if not data: return {}
        eval_data = [d for d in data if d['jaw_tightness'] > 0 or d['oral_stress'] > 0 or d['chin_tremor'] > 0]
        if not eval_data: return {"total_frames": len(data), "evaluable_frames": 0, "frames": data}

        timeline = []
        start_f = eval_data[0]['frame_num']
        curr_state = f"{eval_data[0]['lip_status']}-{eval_data[0]['jaw_status']}-{'DIS' if eval_data[0]['lip_disappear'] else 'OK'}"
        for i in range(1, len(eval_data)):
            state = f"{eval_data[i]['lip_status']}-{eval_data[i]['jaw_status']}-{'DIS' if eval_data[i]['lip_disappear'] else 'OK'}"
            if state != curr_state:
                timeline.append({"start_frame": start_f, "end_frame": eval_data[i-1]['frame_num'], "lip_status": curr_state.split('-')[0], "jaw_status": curr_state.split('-')[1], "lip_disappear": curr_state.split('-')[2] == 'DIS'})
                start_f = eval_data[i]['frame_num']; curr_state = state
        timeline.append({"start_frame": start_f, "end_frame": eval_data[-1]['frame_num'], "lip_status": curr_state.split('-')[0], "jaw_status": curr_state.split('-')[1], "lip_disappear": curr_state.split('-')[2] == 'DIS'})

        return {
            "total_frames": len(data), "evaluable_frames": len(eval_data),
            "averages": {
                "jaw_tightness": round(float(np.mean([d['jaw_tightness'] for d in eval_data])), 1),
                "oral_stress": round(float(np.mean([d['oral_stress'] for d in eval_data])), 1),
                "chin_tremor": round(float(np.mean([d['chin_tremor'] for d in eval_data])), 1)
            },
            "durations": {
                "lip_tensed_percent": round((sum(1 for d in eval_data if d['lip_status'] == 'TENSED') / len(eval_data)) * 100, 1),
                "jaw_tensed_percent": round((sum(1 for d in eval_data if d['jaw_status'] == 'TENSED') / len(eval_data)) * 100, 1),
                "lip_disappear_percent": round((sum(1 for d in eval_data if d['lip_disappear']) / len(eval_data)) * 100, 1)
            },
            "timeline": timeline,
            "frames": data
        }

    def _print_report(self, data):
        s = self.get_summary(data)
        print(f"\n[LIP & JAW REPORT] Frames: {s['total_frames']}")