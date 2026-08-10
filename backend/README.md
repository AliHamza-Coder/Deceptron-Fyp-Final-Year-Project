# Deceptron Backend

Deceptron is a deception detection backend. It uses machine learning models to
analyze facial cues, voice stress, and spoken language, then combines the
results into a single deception score.

---

## Key Features

- **Multi-modal analysis**: Combines face/gaze cues, voice (jitter, pitch),
  and language (Llama 3.3) markers. All cues are computed per segment — there
  is no temporal gating.
- **Bilingual reasoning**: Produces explanations in English and Roman Urdu,
  with detection of evasion, contradiction, vagueness, cognitive load,
  distancing language, and over-explanation.
- **Dynamic baseline**: Uses the first 10 seconds of a session as the
  person's "normal behavior" baseline.
- **Conflict and spike detection**: Flags mismatches between modules (e.g.
  calm face but high voice stress).
- **Cognitive load analysis**: Looks for distancing and mental-effort
  language using the Groq NLP module.
- **Session timeline**: Generates a per-second "truth score" for the whole
  video.
- **VAD-based segmentation**: Segments longer than 15 seconds are split
  automatically using `pydub.silence.detect_nonsilent`. The minimum segment
  length is 1.5 seconds, and sub-segments below RMS 0.005 are discarded.
- **Silence handling**: Filtering happens at three levels — a segment RMS
  gate, then the voice analyzer's RMS + peak gate (returns zero scores with
  a "silence" flag), then a pipeline-level check that skips NLP analysis for
  silent segments.
- **Parallel face analysis**: All 6 face analyzers (emotion, eyes, lip/jaw,
  head, asymmetry, touch) run at the same time per segment using
  `ThreadPoolExecutor(max_workers=6)`.
- **Faster silence check**: Replaced the O(n²) autocorrelation-based f0
  estimate with an O(n) RMS + peak amplitude check for silence detection —
  no accuracy regression.

---

## API Endpoints

The backend runs on FastAPI (default: `http://localhost:8000`).

### 1. Full Pipeline Analysis
`POST /analyze/pipeline`
Processes a video file through all modules.
- **Input**: `video` (file), `question` (string)
- **Output**: Full session report with timeline, segments, and bilingual
  reasoning.

### 2. Voice Stress Analysis
`POST /analyze/voice`
Analyzes audio for micro-tremors and stress markers.
- **Input**: `audio` (file)
- **Output**: Stress score, jitter, pitch stability, and confidence level.

### 3. Facial Expression & Gaze
`POST /analyze/face`
Tracks gaze stability, blink rate, and muscle tension.
- **Input**: `video` (file)
- **Output**: Gaze instability score, blink rate spikes, and lip compression
  markers.

### 4. Visual Emotion Recognition
`POST /analyze/emotion`
Detects micro-expressions and primary emotional states.
- **Input**: `video` (file)
- **Output**: Dominant emotion, secondary shifts, and emotional intensity.

---

## Installation & Setup

### Prerequisites
- **Python 3.10+** (virtual environment recommended)
- **[FFmpeg](https://ffmpeg.org/download.html)**: required. FFmpeg must be
  installed and on the Windows PATH.
  - *Test it*: run `ffmpeg -version` in a terminal. If it fails, the app will
    not be able to extract audio.
- **NVIDIA GPU**: recommended for faster facial and voice analysis.

### Configuration
1. Create a `.env` file in the backend root:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Running the Server
```powershell
python server.py
```

---

## Packaging (EXE)

To build a standalone Windows executable that includes all AI models (~180MB)
and dependencies:
1. **Virtual environment**: install your libraries in a folder named `myenv`.
2. **Run the build script**:
   ```powershell
   .\build_backend.ps1
   ```
3. **Standalone EXE**: the result is a single `deceptron_backend.exe` in the
   `dist/` folder. It is portable and handles paths with spaces
   automatically.

---

## Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **FFmpeg error** | Make sure `ffmpeg` is on the System PATH. The app uses it to convert video to audio. |
| **FastAPI not found** | Run the build script with `.\build_backend.ps1`. It forces PyInstaller to use your `myenv` libraries. |
| **Path errors** | Avoid manual quotes in file paths. The backend handles URL-encoded paths and spaces automatically. |
| **Groq API error** | Check your `.env` file. Make sure `GROQ_API_KEY` is valid and you have an internet connection for NLP reasoning. |

---

## Metadata & Architecture
- **Engine**: Llama-3.3-70B (via Groq)
- **Face/Emotion**: Local Torch/MediaPipe models (~100MB)
- **Voice**: Local Whisper/Pyannote models (~80MB)
- **Persistence**: Reports and logs are saved to `~/.deceptron/results/`.
- **Recordings**: Session recordings (.mp4) are managed via the frontend and
  stored in `~/.deceptron/recordings/`.
