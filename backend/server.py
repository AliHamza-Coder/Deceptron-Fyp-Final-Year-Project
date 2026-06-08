import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ========================================
# DECEPTRON BACKEND - MODULAR SERVER
# ========================================

# 1. Path Configuration
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Running in a normal Python environment
    BASE_DIR = Path(__file__).resolve().parent

MODULES_DIR = BASE_DIR / "modules"
sys.path.append(str(MODULES_DIR))

# Persistence paths
DATA_DIR = Path.home() / ".deceptron"
RESULTS_DIR = DATA_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 2. Initialize FastAPI
app = FastAPI(
    title="Deceptron Modular API",
    description="Professional Forensic Analysis Suite",
    version="4.0.0"
)

# 3. Setup Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Mount Static Files (Results and Data)
app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

# 5. Import and Register Modular Routes
from api.routes import voice, emotion, face, pipeline

app.include_router(voice.router)
app.include_router(emotion.router)
app.include_router(face.router)
app.include_router(pipeline.router)

# 6. Root Status
@app.get("/")
async def status():
    return {
        "status": "online",
        "mode": "Modular Architecture",
        "modules": ["voice", "emotion", "face", "pipeline"],
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("DECEPTRON MODULAR BACKEND IS READY")
    print("   Endpoints: /analyze/voice, /analyze/emotion, /analyze/face, /analyze/pipeline")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
