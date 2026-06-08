from fastapi import APIRouter, Form, Query
import os
import json
import uuid
from pathlib import Path
import traceback

router = APIRouter(prefix="/analyze", tags=["Forensics"])

# Persistence paths
DATA_DIR = Path.home() / ".deceptron"

import urllib.parse

def resolve_path(file_path: str):
    # Handle URL encoding (e.g. %20 for spaces)
    file_path = urllib.parse.unquote(file_path)
    
    if file_path.startswith("/data/"):
        p = str(DATA_DIR / file_path.replace("/data/", "", 1))
    else:
        p = file_path
    
    # Final cleanup: unquote, strip quotes, and use forward slashes for FFmpeg compatibility
    p = urllib.parse.unquote(p.strip('"').strip("'"))
    return Path(p).as_posix()

@router.get("/pipeline")
@router.post("/pipeline")
async def analyze_pipeline(
    file_path: str = Query(None), 
    path_form: str = Form(None), 
    audio_path: str = Query(None), 
    audio_form: str = Form(None)
):
    video_path = file_path or path_form
    if not video_path:
        return {"success": False, "message": "No video file path provided"}
    
    audio_path_final = audio_path or audio_form
    
    try:
        physical_video = resolve_path(video_path)
        physical_audio = resolve_path(audio_path_final) if audio_path_final else None
        
        from deception_pipeline import DeceptionPipeline
        
        # Ensure output directories exist
        report_dir = DATA_DIR / "reports"
        video_dir = DATA_DIR / "results"
        report_dir.mkdir(parents=True, exist_ok=True)
        video_dir.mkdir(parents=True, exist_ok=True)
        
        # Run the full deception pipeline
        pipeline = DeceptionPipeline(report_dir=str(report_dir), video_dir=str(video_dir))
        report_path = pipeline.process(physical_video, physical_audio, question_context="")
        
        if report_path and os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
                
            return {
                "success": True,
                "type": "pipeline",
                "session_id": report_data.get("session_id", str(uuid.uuid4())[:8]),
                "data": report_data
            }
        else:
            return {"success": False, "message": "Pipeline completed but no report was generated."}
            
    except Exception as e:
        print("Pipeline API Error:")
        traceback.print_exc()
        return {"success": False, "message": str(e)}
