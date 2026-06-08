from fastapi import APIRouter, Form, Query
import os
import uuid
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/analyze", tags=["Vision"])

# Persistence paths
DATA_DIR = Path.home() / ".deceptron"
RESULTS_DIR = DATA_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

import urllib.parse

def resolve_path(file_path: str):
    if file_path.startswith("/data/"):
        p = str(DATA_DIR / file_path.replace("/data/", "", 1))
    else:
        p = file_path
    
    p = urllib.parse.unquote(p.strip('"').strip("'"))
    return Path(p).as_posix()

from emotion_detection_module import EmotionAnalyzer
analyzer = EmotionAnalyzer()

@router.get("/emotion")
@router.post("/emotion")
async def analyze_emotion(file_path: str = Query(None), path_form: str = Form(None)):
    path = file_path or path_form
    if not path:
        return {"success": False, "message": "No file path provided"}
    
    try:
        physical_path = resolve_path(path)
        if not os.path.exists(physical_path):
            return {"success": False, "message": f"File not found: {physical_path}"}

        u_id = str(uuid.uuid4())[:6]
        orig_name = os.path.basename(physical_path).split('.')[0]
        output_filename = f"res_{u_id}_{orig_name}.mp4"
        output_path = str(RESULTS_DIR / output_filename)

        print(f"API: Analyzing Emotion for {physical_path}")
        
        frame_data = analyzer.process_video(physical_path, output_path=output_path, verbose=False)
        summary = analyzer.get_summary(frame_data)
        
        return {
            "success": True,
            "type": "emotion",
            "session_id": u_id,
            "timestamp": datetime.now().isoformat(),
            "video_url": f"/data/results/{output_filename}",
            "summary": summary,
            "frames": frame_data  # This gives you the frame-by-frame data for graphs
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
