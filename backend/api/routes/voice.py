from fastapi import APIRouter, Form, Query
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/analyze", tags=["Forensics"])

# Persistence paths
DATA_DIR = Path.home() / ".deceptron"

import urllib.parse
import subprocess
import tempfile
from forensic_voice_analyzer import ForensicVoiceAnalyzer
import soundfile as sf

# Pre-load analyzer for speed
analyzer = ForensicVoiceAnalyzer()

def resolve_path(file_path: str):
    if file_path.startswith("/data/"):
        p = str(DATA_DIR / file_path.replace("/data/", "", 1))
    else:
        p = file_path
    
    p = urllib.parse.unquote(p.strip('"').strip("'"))
    return Path(p).as_posix()

@router.get("/voice")
@router.post("/voice")
async def analyze_voice(file_path: str = Query(None), path_form: str = Form(None)):
    path = file_path or path_form
    if not path:
        return {"success": False, "message": "No file path provided"}
    
    try:
        physical_path = resolve_path(path)
        
        # Check if it's a video file - soundfile can't read mp4 directly
        if physical_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            print(f"Voice: Video detected. Extracting audio from {physical_path}")
            temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
            subprocess.run([
                "ffmpeg", "-y", "-i", physical_path, 
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", 
                temp_wav
            ], check=True, capture_output=True)
            wav_to_analyze = temp_wav
            is_temp = True
        else:
            wav_to_analyze = physical_path
            is_temp = False

        data, samplerate = sf.read(wav_to_analyze)
        duration = len(data) / samplerate
        metrics = analyzer.analyze_segment(wav_to_analyze, 0, duration)
        
        # Cleanup temp file
        if is_temp and os.path.exists(temp_wav):
            os.remove(temp_wav)

        return {
            "success": True,
            "type": "voice",
            "session_id": str(uuid.uuid4())[:8],
            "filename": os.path.basename(physical_path),
            "data": metrics
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
