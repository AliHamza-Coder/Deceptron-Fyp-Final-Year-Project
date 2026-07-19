import cv2
import mediapipe as mp
import numpy as np
import os
from collections import defaultdict

class HandFaceTouchAnalyzer:
    """Detects hand-to-face touches (self-adaptors) with high accuracy using scaling radius logic."""

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_draw = mp.solutions.drawing_utils
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Precise Landmark Clusters (Optimized for Forensic Accuracy)
        self.NOSE_REGION = [1, 2, 5, 168, 19, 94, 4, 6, 197, 195] # Comprehensive nose coverage
        self.MOUTH_REGION = [0, 13, 14, 17, 37, 267, 61, 291, 78, 308, 11, 12] # Lips and philtrum
        self.FOREHEAD = 10
        self.EYES_REGION = [33, 133, 157, 158, 159, 160, 161, 263, 362, 384, 385, 386, 387, 388]
        self.LEFT_CHEEK = 117
        self.RIGHT_CHEEK = 346
        self.CHIN_REGION = [152, 148, 149, 150, 175, 377, 378, 379]

        # Finger tip indices (Index, Middle, Ring, Pinky tips)
        self.FINGER_TIPS = [8, 12, 16, 20]

    def _landmark_point(self, landmarks, idx, img_w, img_h):
        if isinstance(idx, (tuple, list)):
            pts = np.array([(landmarks[i].x * img_w, landmarks[i].y * img_h) for i in idx])
            return np.mean(pts, axis=0)
        lm = landmarks[idx]
        return np.array([lm.x * img_w, lm.y * img_h])

    def _distance(self, pt1, pt2):
        return np.linalg.norm(np.array(pt1) - np.array(pt2))

    def _get_regions_def(self, landmarks, img_w, img_h):
        """Returns map of region name to (center_pt, radius)."""
        l_eye = landmarks[33]
        r_eye = landmarks[263]
        chin = landmarks[152]
        nose = landmarks[1]
        
        face_w = abs(r_eye.x - l_eye.x) * img_w
        face_h = abs(chin.y - nose.y) * img_h
        baselen = min(face_w, face_h)

        # Region configuration with optimized radii to prevent overlap
        radii = {
            'NOSE': 0.05 * baselen,
            'MOUTH': 0.06 * baselen,
            'EYES': 0.05 * baselen,
            'FOREHEAD': 0.06 * baselen,
            'CHEEK': 0.07 * baselen,
            'CHIN': 0.06 * baselen
        }
        
        return {
            'NOSE': (self._landmark_point(landmarks, self.NOSE_REGION, img_w, img_h), radii['NOSE']),
            'MOUTH': (self._landmark_point(landmarks, self.MOUTH_REGION, img_w, img_h), radii['MOUTH']),
            'FOREHEAD': (self._landmark_point(landmarks, self.FOREHEAD, img_w, img_h), radii['FOREHEAD']),
            'CHIN': (self._landmark_point(landmarks, self.CHIN_REGION, img_w, img_h), radii['CHIN']),
            'EYES': (self._landmark_point(landmarks, self.EYES_REGION, img_w, img_h), radii['EYES']),
            'LEFT_CHEEK': (self._landmark_point(landmarks, self.LEFT_CHEEK, img_w, img_h), radii['CHEEK']),
            'RIGHT_CHEEK': (self._landmark_point(landmarks, self.RIGHT_CHEEK, img_w, img_h), radii['CHEEK'])
        }

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
            fourcc = cv2.VideoWriter_fourcc(*'H264'); out = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))
            
        frame_data, frame_idx = [], 0
        touch_duration = 0

        while True:
            ret, frame = cap.read()
            if not ret: break
            frame_idx += 1
            if frame_idx < start_frame: continue
            if frame_idx > end_frame: break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h_res = self.hands.process(rgb)
            f_res = self.face_mesh.process(rgb)
            
            touches = []
            touch_conf = 0.0
            regions_def = {}
            
            if f_res.multi_face_landmarks:
                landmarks = f_res.multi_face_landmarks[0].landmark
                regions_def = self._get_regions_def(landmarks, width, height)

                if h_res.multi_hand_landmarks:
                    for h_lms in h_res.multi_hand_landmarks:
                        for tip_idx in self.FINGER_TIPS:
                            tip_pt = np.array([h_lms.landmark[tip_idx].x * width, h_lms.landmark[tip_idx].y * height])
                            
                            best_region = None
                            min_dist = float('inf')
                            
                            for r_name, (r_pt, r_radius) in regions_def.items():
                                dist = self._distance(tip_pt, r_pt)
                                if dist <= r_radius and dist < min_dist:
                                    min_dist = dist
                                    best_region = r_name
                            
                            if best_region:
                                if best_region not in touches: 
                                    touches.append(best_region)
                                r_radius = regions_def[best_region][1]
                                touch_conf = max(touch_conf, (1.0 - min_dist / r_radius) * 100)
                        
                        if out:
                            self.mp_draw.draw_landmarks(frame, h_lms, self.mp_hands.HAND_CONNECTIONS)

                if out:
                    for r_name, (r_pt, r_radius) in regions_def.items():
                        color = (0,0,255) if r_name in touches else (0,255,0)
                        cv2.circle(frame, (int(r_pt[0]), int(r_pt[1])), int(r_radius), color, 1)
                        if r_name in touches:
                            cv2.putText(frame, r_name, (int(r_pt[0]), int(r_pt[1])-10), 0, 0.4, (0,0,255), 1)

            if touches:
                touch_duration += 1
            else:
                touch_duration = 0

            if out: out.write(cv2.resize(frame, (out_w, out_h)) if scale != 1.0 else frame)
            frame_data.append({
                'frame_num': frame_idx, 
                'timestamp': frame_idx/fps, 
                'touches': touches, 
                'confidence': round(touch_conf, 2),
                'duration': touch_duration
            })
            if verbose and frame_idx % 30 == 0: print(f"Touch Processed: {frame_idx}/{end_frame}")

        cap.release()
        if out: out.release()
        return frame_data

    def get_summary(self, data):
        if not data: return {}
        all_touches = [t for d in data for t in d['touches']]
        counts = {r: all_touches.count(r) for r in set(all_touches)}
        
        timeline = []
        if data:
            start_f = data[0]['frame_num']
            curr_t = sorted(data[0]['touches'])
            for i in range(1, len(data)):
                t = sorted(data[i]['touches'])
                if t != curr_t:
                    if curr_t:
                        timeline.append({"start_frame": start_f, "end_frame": data[i-1]['frame_num'], "regions": curr_t})
                    start_f = data[i]['frame_num']; curr_t = t
            if curr_t:
                timeline.append({"start_frame": start_f, "end_frame": data[-1]['frame_num'], "regions": curr_t})

        return {
            "total_frames": len(data),
            "touch_count": len([d for d in data if d['touches']]),
            "region_distribution": counts,
            "timeline": timeline,
            "frames": data
        }

    def _print_report(self, data):
        s = self.get_summary(data)
        print(f"\n[TOUCH REPORT] Frames with Touch: {s['touch_count']} / {s['total_frames']}")
        for r, c in s['region_distribution'].items(): print(f"  {r}: {c} frames")

if __name__ == "__main__":
    path = input("Video Path: ").strip().strip('"')
    if os.path.exists(path):
        analyzer = HandFaceTouchAnalyzer()
        res = analyzer.process_video(path, output_path="touch_output.mp4")
        analyzer._print_report(res)