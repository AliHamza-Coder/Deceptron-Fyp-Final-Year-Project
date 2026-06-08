# 👁️ Deceptron Backend - Forensic Intelligence Suite

Deceptron is a modular, professional-grade forensic deception detection backend. It leverages state-of-the-art machine learning models for facial analysis, vocal stress detection, and linguistic profiling to provide high-confidence forensic insights.

---

## 🚀 Key Features

*   **Multi-Modal Fusion**: Combines Visual (Face/Gaze), Vocal (Jitter/Pitch), and Linguistic (Llama 3.3) markers. No temporal gating — all cues instantaneous.
*   **Bilingual Forensic Reasoning**: Generates complex behavioral verdicts in both **English** and **Roman Urdu** with `max_tokens=2048` and NLQ flag detection (evasion, contradiction, vagueness, cognitive_load, distancing_language, over_explanation).
*   **Dynamic Baselines**: Automatically establishes a 10-second "Normal Behavior" baseline for every suspect.
*   **Conflict & Spike Detection**: Flags mismatches between modules (e.g., "Calm Face" but "High Voice Stress").
*   **Cognitive Load Analysis**: Detects linguistic distancing and mental effort markers using Groq-powered NLP.
*   **Session Timeline**: Provides a second-by-second "Truth Score" for data visualization.
*   **VAD-Based Segmentation**: Long segments (>15s) automatically split via `pydub.silence.detect_nonsilent`. Minimum segment: 1.5s. Sub-segments below RMS 0.005 discarded.
*   **3-Layer Silence Shield**: Multi-tier silence filtering — segment RMS gate → voice analyzer RMS+peak gate (`_silence_result()` returns zero scores with "silence" flag) → pipeline flag+transcription check skips NLQ entirely.
*   **Parallel Face Analysis**: All 6 face analyzers (emotion, eyes, lip/jaw, head, asymmetry, touch) run concurrently per segment via `ThreadPoolExecutor(max_workers=6)`.
*   **Optimized Voice Pipeline**: Replaced O(n²) autocorrelation-based `_rough_f0_energy` with O(n) RMS + peak amplitude check for silence detection — no accuracy regression.

---

## 📍 API Endpoints

The backend runs on **FastAPI** (Default: `http://localhost:8000`).

### 1. Full Pipeline Analysis
`POST /analyze/pipeline`
Processes a video file through all forensic modules.
*   **Input**: `video` (file), `question` (string)
*   **Output**: Full session report with timeline, segments, and bilingual reasoning.

### 2. Vocal Stress Analysis
`POST /analyze/voice`
Analyzes audio for micro-tremors and stress markers.
*   **Input**: `audio` (file)
*   **Output**: Stress score, jitter, pitch stability, and confidence level.

### 3. Facial Expression & Gaze
`POST /analyze/face`
Tracks gaze stability, blink rate, and muscle tension.
*   **Input**: `video` (file)
*   **Output**: Gaze instability score, blink rate spikes, and lip compression markers.

### 4. Visual Emotion Recognition
`POST /analyze/emotion`
Detects micro-expressions and primary emotional states.
*   **Input**: `video` (file)
*   **Output**: Dominant emotion, secondary shifts, and emotional intensity.

---

---

## 🛠️ Installation & Setup

### Prerequisites
*   **Python 3.10+** (Virtual environment recommended)
*   **[FFmpeg](https://ffmpeg.org/download.html)**: **CRITICAL.** FFmpeg must be installed and added to your Windows PATH. 
    *   *Test it*: Run `ffmpeg -version` in PowerShell. If it fails, the app will not extract audio.
*   **NVIDIA GPU**: Recommended for faster facial and voice analysis.

### Configuration
1.  Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_api_key_here
    ```
2.  Install dependencies:
    ```powershell
    pip install -r requirements.txt
    ```

### Running the Server
```powershell
python server.py
```

---

## 📦 Packaging (EXE)

To build a standalone Windows executable that includes all AI models (~180MB) and dependencies:
1.  **Virtual Environment**: Ensure your libraries are installed in a folder named `myenv`.
2.  **Run Build Script**:
    ```powershell
    .\build_backend.ps1
    ```
3.  **Standalone EXE**: The result is a single `deceptron_backend.exe` in the `dist/` folder. It is portable and handles paths with spaces automatically.

---

## 💡 Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **FFmpeg Error** | Ensure `ffmpeg` is in your System PATH. The app uses it to convert video to audio. |
| **FastAPI Not Found** | Run the build script using `.\build_backend.ps1`. It forces PyInstaller to use your `myenv` libraries. |
| **Path Errors** | Avoid manual quotes in file paths. The backend handles URL-encoded paths and spaces automatically. |
| **Groq API Error** | Check your `.env` file. Ensure `GROQ_API_KEY` is valid and you have an internet connection for NLP reasoning. |

---

## 📑 Metadata & Architecture
*   **Engine**: Llama-3.3-70B (via Groq)
*   **Face/Emotion**: Local Torch/MediaPipe models (~100MB)
*   **Voice**: Local Whisper/Pyannote models (~80MB)
*   **Persistence**: Reports and logs are saved to `~/.deceptron/results/`.
*   **Forensic Evidence**: Recorded sessions (.mp4) are managed via the frontend and stored in `~/.deceptron/recordings/`.

---

**Developed by Antigravity AI for Deceptron FYP.**
