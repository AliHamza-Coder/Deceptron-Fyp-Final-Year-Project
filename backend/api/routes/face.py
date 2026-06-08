from fastapi import APIRouter, Form, Query, HTTPException
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime
import traceback
import cv2

# Setup robust paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent # Points to 'backend'
MODULES_DIR = BASE_DIR / "modules"
if str(MODULES_DIR) not in sys.path:
    sys.path.append(str(MODULES_DIR))

router = APIRouter(prefix="/analyze", tags=["Forensics - Vision"])

# Persistence paths
DATA_DIR = Path.home() / ".deceptron"
RESULTS_DIR = DATA_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

import urllib.parse
from eye_gaze_module import EyeGazeAnalyzer
from head_pose_module import HeadPoseAnalyzer
from lip_jaw_module import LipJawAnalyzer
from asymmetry_module import AsymmetryAnalyzer
from hand_face_touch_module import HandFaceTouchAnalyzer
from emotion_detection_module import EmotionAnalyzer

# Pre-load for high performance
eye_analyzer = EyeGazeAnalyzer()
pose_analyzer = HeadPoseAnalyzer()
lip_analyzer = LipJawAnalyzer()
asym_analyzer = AsymmetryAnalyzer()
touch_analyzer = HandFaceTouchAnalyzer()
emotion_analyzer = EmotionAnalyzer()

def resolve_path(file_path: str):
    if not file_path: return ""
    if file_path.startswith("/data/"):
        p = str(DATA_DIR / file_path.replace("/data/", "", 1))
    else:
        p = file_path
    
    p = urllib.parse.unquote(p.strip('"').strip("'"))
    return Path(p).as_posix()

def run_analysis(analyzer, file_path, prefix, orig_name, u_id):
    try:
        out_filename = f"{prefix}_{u_id}_{orig_name}.mp4"
        output_path = str(RESULTS_DIR / out_filename)
        # Calculate 720p scale
        cap = cv2.VideoCapture(file_path)
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        scale = min(720.0 / h, 1.0) if h > 0 else 1.0
        data = analyzer.process_video(file_path, output_path=output_path, verbose=False, scale=scale)
        summary = analyzer.get_summary(data)
        return summary, out_filename
    except Exception as e:
        print(f"Error in {prefix} analysis: {str(e)}")
        traceback.print_exc()
        raise e

@router.get("/face/gaze")
@router.post("/face/gaze")
async def analyze_gaze(file_path: str = Query(None), path_form: str = Form(None)):
    path = resolve_path(file_path or path_form)
    if not os.path.exists(path): return {"success": False, "message": f"File not found: {path}"}
    try:
        u_id = str(uuid.uuid4())[:6]
        orig_name = os.path.basename(path).split('.')[0]
        summary, video = run_analysis(eye_analyzer, path, "gaze", orig_name, u_id)
        return {"success": True, "type": "gaze", "summary": summary, "video_url": f"/data/results/{video}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/face/pose")
@router.post("/face/pose")
async def analyze_pose(file_path: str = Query(None), path_form: str = Form(None)):
    path = resolve_path(file_path or path_form)
    if not os.path.exists(path): return {"success": False, "message": f"File not found: {path}"}
    try:
        u_id = str(uuid.uuid4())[:6]
        orig_name = os.path.basename(path).split('.')[0]
        summary, video = run_analysis(pose_analyzer, path, "pose", orig_name, u_id)
        return {"success": True, "type": "pose", "summary": summary, "video_url": f"/data/results/{video}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/face/touch")
@router.post("/face/touch")
async def analyze_touch(file_path: str = Query(None), path_form: str = Form(None)):
    path = resolve_path(file_path or path_form)
    if not os.path.exists(path): return {"success": False, "message": f"File not found: {path}"}
    try:
        u_id = str(uuid.uuid4())[:6]
        orig_name = os.path.basename(path).split('.')[0]
        summary, video = run_analysis(touch_analyzer, path, "touch", orig_name, u_id)
        return {"success": True, "type": "touch", "summary": summary, "video_url": f"/data/results/{video}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/face/lipjaw")
@router.post("/face/lipjaw")
async def analyze_lipjaw(file_path: str = Query(None), path_form: str = Form(None)):
    path = resolve_path(file_path or path_form)
    if not os.path.exists(path): return {"success": False, "message": f"File not found: {path}"}
    try:
        u_id = str(uuid.uuid4())[:6]
        orig_name = os.path.basename(path).split('.')[0]
        summary, video = run_analysis(lip_analyzer, path, "lipjaw", orig_name, u_id)
        return {"success": True, "type": "lipjaw", "summary": summary, "video_url": f"/data/results/{video}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/face/asymmetry")
@router.post("/face/asymmetry")
async def analyze_asymmetry(file_path: str = Query(None), path_form: str = Form(None)):
    path = resolve_path(file_path or path_form)
    if not os.path.exists(path): return {"success": False, "message": f"File not found: {path}"}
    try:
        u_id = str(uuid.uuid4())[:6]
        orig_name = os.path.basename(path).split('.')[0]
        summary, video = run_analysis(asym_analyzer, path, "asym", orig_name, u_id)
        return {"success": True, "type": "asymmetry", "summary": summary, "video_url": f"/data/results/{video}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/face/emotion")
@router.post("/face/emotion")
async def analyze_emotion(file_path: str = Query(None), path_form: str = Form(None)):
    path = resolve_path(file_path or path_form)
    if not os.path.exists(path): return {"success": False, "message": f"File not found: {path}"}
    try:
        u_id = str(uuid.uuid4())[:6]
        orig_name = os.path.basename(path).split('.')[0]
        summary, video = run_analysis(emotion_analyzer, path, "emotion", orig_name, u_id)
        return {"success": True, "type": "emotion", "summary": summary, "video_url": f"/data/results/{video}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

import asyncio

@router.get("/face")
@router.post("/face")
async def analyze_face_full(file_path: str = Query(None), path_form: str = Form(None)):
    path = resolve_path(file_path or path_form)
    if not os.path.exists(path): return {"success": False, "message": f"File not found: {path}"}
    
    try:
        u_id = str(uuid.uuid4())[:6]
        orig_name = os.path.basename(path).split('.')[0]
        
        # Parallel Execution for High Performance
        tasks = [
            asyncio.to_thread(run_analysis, eye_analyzer, path, "gaze", orig_name, u_id),
            asyncio.to_thread(run_analysis, pose_analyzer, path, "pose", orig_name, u_id),
            asyncio.to_thread(run_analysis, lip_analyzer, path, "lipjaw", orig_name, u_id),
            asyncio.to_thread(run_analysis, asym_analyzer, path, "asym", orig_name, u_id),
            asyncio.to_thread(run_analysis, touch_analyzer, path, "touch", orig_name, u_id),
            asyncio.to_thread(run_analysis, emotion_analyzer, path, "emotion", orig_name, u_id)
        ]
        
        # Run all modules simultaneously
        results_list = await asyncio.gather(*tasks)
        
        # Unpack results
        (g_sum, g_vid), (p_sum, p_vid), (l_sum, l_vid), (a_sum, a_vid), (h_sum, h_vid), (e_sum, e_vid) = results_list

        return {
            "success": True,
            "session_id": u_id,
            "timestamp": datetime.now().isoformat(),
            "results": {
                "eye_gaze": {"summary": g_sum, "video": f"/data/results/{g_vid}"},
                "head_pose": {"summary": p_sum, "video": f"/data/results/{p_vid}"},
                "lip_jaw": {"summary": l_sum, "video": f"/data/results/{l_vid}"},
                "asymmetry": {"summary": a_sum, "video": f"/data/results/{a_vid}"},
                "hand_touch": {"summary": h_sum, "video": f"/data/results/{h_vid}"},
                "emotion": {"summary": e_sum, "video": f"/data/results/{e_vid}"}
            }
        }
    except Exception as e:
        print(f"Full Analysis Error: {str(e)}")
        traceback.print_exc()
        return {"success": False, "message": str(e)}
