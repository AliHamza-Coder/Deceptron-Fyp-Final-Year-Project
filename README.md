# Deceptron — Forensic Multi-Modal Deception Detection Platform

**Version:** 1.4.0 Enterprise  
**Lead Developer:** Ali Hamza  
**Type:** Final Year Project (FYP) — Desktop Forensic Application  
**Repository:** `Deceptron-Fyp-Final-Year-Project`

---

## Overview

Deceptron is an advanced forensic deception detection system that combines multi-modal behavioral analysis—facial micro-expressions, vocal stress patterns, and linguistic deception indicators—into a unified scoring engine. It processes live or pre-recorded video/audio interviews through a modular pipeline of AI/ML components and presents forensically-graded results via a desktop interface.

The system is designed for investigative and research use cases where behavioral baseline comparison, speaker diarization, and cross-modal conflict detection are required to assess truthfulness with quantified confidence levels.

---

## Tech Stack

### Backend — AI / ML Pipeline
| Component | Technology |
|-----------|-----------|
| Server Framework | FastAPI (Python 3.9+) |
| Deep Learning | PyTorch 2.8.0, TorchVision 0.23.0 |
| Face Mesh / Detection | MediaPipe |
| Facial Emotion | HSEmotion |
| Speaker Diarization | PyAnnote Audio (offline pipeline) |
| Speech-to-Text | OpenAI Whisper (base model, offline-capable) |
| Acoustic Analysis | Parselmouth / Praat |
| Audio Processing | LibROSA, SoundFile, NumPy |
| LLM Deception Analysis | Groq API — Llama-3.3-70B-Versatile |
| Video Processing | FFmpeg, OpenCV |

### Frontend — Desktop UI
| Component | Technology |
|-----------|-----------|
| Desktop Bridge | Eel (Python–JavaScript) |
| UI Language | Vanilla JavaScript (ES6) + HTML5 |
| Styling | Custom "Forensic Neon" Design System (CSS Variables) |
| Charts | Chart.js |
| Audio Visualization | WaveSurfer.js |
| Icons | Font Awesome |
| Database | TinyDB (local JSON storage) |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Authentication | SHA-256 + Salt hashing, session-managed |
| Persistence | TinyDB (`~/.deceptron/db.json`) |
| File Storage | `~/.deceptron/results/`, `~/.deceptron/reports/` |
| Build / Packaging | PyInstaller (desktop executable support) |

---

## Features

### 1. Live Session Analysis
Real-time behavioral capture from webcam and microphone during interview sessions. Supports both live recording and pre-recorded file analysis. Chunked file upload (1MB chunks) for large media files. Toggle between live-stream and file-based analysis modes.

### 2. Facial Micro-Expression Analysis
Five concurrent face-analysis modules extract behavioral cues from video:
- **Eye Gaze Tracking** — Blink rate, gaze stability, direction changes, fixation score, blink spike detection
- **Head Pose Estimation** — Pitch / yaw / roll angles, withdrawal score, stiffness, nodding and shaking detection
- **Lip & Jaw Tension** — Jaw tightness, lip compression, chin tremor, lip disappearance
- **Facial Asymmetry** — Mouth, brow, and eye asymmetry relative to behavioral baseline
- **Hand-to-Face Touch Detection** — Self-adaptor gesture recognition with duration tracking

### 3. Facial Emotion Recognition
Real-time emotion classification using HSEmotion. Detects and timestamps dominant emotions across the session timeline. Emotion variance and controlled-expression scoring feed into the fusion engine.

### 4. Forensic Voice Stress Analysis
Acoustic feature extraction using Praat and pure-NumPy signal processing:
- **Fundamental Frequency (F0)** — mean, std, min, max, stability classification (Flat / Stable / Unstable)
- **Micro-Tremors** — jitter (local, ppq5), shimmer (local, apq11), stability score
- **Spectral Clarity** — HNR (Harmonics-to-Noise Ratio), spectral centroid
- **Temporal Dynamics** — speaking rate (WPM, syllables/sec), pause ratio, hesitation detection
- **Energy Profile** — RMS energy trend, zero-crossing rate
- **Stress Categories** — Low / Moderate / High-Controlled / High-Genuine / Critical
- **Bilingual Transcription** — Whisper provides original-language transcription and English translation per segment

### 5. NLP Deception Analysis (LLM-Powered)
Groq-hosted Llama-3.3-70B-Versatile analyzes spoken transcripts for 8 forensic linguistics indicators:
- **Evasion** — non-answers, topic changes
- **Over-explanation** — unnecessary specificity for credibility
- **Irrelevance** — semantic drift
- **Contradiction** — intra-response self-contradiction
- **Vagueness** — hedge language, uncertain phrasing
- **Improbable Details** — unrealistic precision (timestamps, trivial memories)
- **Cognitive Load** — filler-word density, rambling sentence structure
- **Distancing Language** — impersonal pronoun avoidance
- **Emotion Mismatch** — cross-modal conflict with voice stress
- **Bilingual Support** — English, Roman Urdu, and Urdu input; Roman Urdu + English output summaries
- **Cross-Segment Contradiction** — compares current answer against previous 3 segments
- **Smart Caching** — MD5-hashed result cache to reduce redundant API calls

### 6. Automatic Speaker Diarization
PyAnnote Audio identifies who spoke when, automatically labeling the primary suspect (longest-speaking speaker) and interviewer. Enables question-to-answer linkage without manual annotation.

### 7. Question-Answer Segmentation
Combines diarization with Whisper transcription to extract suspect answer segments. Long responses (>15 seconds) are automatically split using silence-based VAD into sub-segments for granular per-turn analysis.

### 8. Multi-Modal Fusion Engine
The core decision layer combines all modalities using weighted psychological rules:
| Modality | Weight |
|----------|--------|
| Face Behavioral Cues | 35% |
| Face Emotion (controlled) | 10% |
| Voice Stress | 25% |
| NLP Deception | 25% |
| Cross-Modal Mismatch | 5% |

- **Bonus Rules** — multi-cue clustering bonus (+15), NLP + lip-disappear confirmation (+10)
- **Conflict Detection** — flags mismatches (e.g., neutral face + high voice stress)
- **Spike Detection** — detects sudden behavioral changes vs. baseline
- **Veracity Verdict** — LOW / MEDIUM / HIGH / CRITICAL confidence with bilingual explanation

### 9. Behavioral Baseline Calibration
Establishes a subject-specific normal-behavior baseline from the first 10 seconds of video. All subsequent cues are normalized against this baseline for personalized assessment.

### 10. Case Report Generation
JSON and visual forensic reports generated per session, including:
- Final deception score with confidence level and verdict
- Per-module score breakdown
- Active cues list with severity, timestamp, and duration
- Cross-modal flags and temporal summary
- Annotated video output saved to `~/.deceptron/results/`
- 2×2 combined presentation video generation

### 11. Evidence Vault (Media Management)
- Chunked upload for large video / audio files
- Type-based filtering (video / audio)
- Media preview with WaveSurfer.js audio player
- Download and delete capabilities
- Upload metadata tracking per user

### 12. Trend Analytics Dashboard
- Doughnut chart showing High-Risk / Ambiguous / Trustworthy case distribution
- Recent analysis history table with color-coded risk indicators
- Case count counter and per-report risk score calculation
- Real-time data refresh via TinyDB queries

### 13. User Account System
- Secure registration and login (SHA-256 + salt)
- Profile management with avatar support
- Session persistence across application restarts

### 14. Profile & Settings Management
- Editable user profile (name, username, avatar)
- Settings page for application preferences

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Deceptron Desktop Application                  │
│                    (Eel + Vanilla JS Frontend)                   │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│   Login /    │   Start      │   Evidence   │   Case Reports     │
│   Signup     │   Session    │   Vault      │   & History        │
│              │   (Live)     │   (Uploads)  │                    │
├──────────────┴──────────────┴──────────────┴────────────────────┤
│                         FastAPI Backend                          │
│                    (Port 8000 / Modular Routes)                  │
├────────────────┬────────────────┬────────────────────────────────┤
│  Voice         │  Emotion       │  Face (Gaze / Pose /          │
│  Analyzer      │  Detector      │   Lip-Jaw / Asymmetry /       │
│  (Whisper +    │  (HSEmotion)   │   Hand-Touch)                  │
│  Praat)        │                │  (MediaPipe)                   │
├────────────────┴────────────────┴────────────────────────────────┤
│              Speaker Diarizer (PyAnnote) + Segment Manager        │
│              NLP Deception (Groq LLM) + Fusion Engine            │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   TinyDB          │
                    │   (~/.deceptron/) │
                    └──────────────────┘
```

---

## Project Structure

```
Deceptron-Fyp-Final-Year-Project/
├── README.md
├── backend/
│   ├── server.py                          # FastAPI entry point & route registration
│   ├── requirements.txt                   # 143 Python dependencies
│   ├── .env.example                       # Groq API key template
│   ├── download_models.py                 # Offline model downloader
│   ├── build_backend.ps1                  # Backend build script
│   ├── deceptron_backend.spec             # PyInstaller spec (backend)
│   └── modules/
│       ├── main.py                        # Pipeline CLI entry
│       ├── speaker_diarizer.py            # PyAnnote speaker identification
│       ├── segment_manager.py             # Q&A segmentation + VAD
│       ├── forensic_voice_analyzer.py     # Praat acoustic + Whisper transcription
│       ├── emotion_detection_module.py    # HSEmotion realtime classification
│       ├── eye_gaze_module.py             # MediaPipe gaze / blink tracking
│       ├── head_pose_module.py            # Head pose angles & gestures
│       ├── lip_jaw_module.py              # Lip/jaw tension analysis
│       ├── asymmetry_module.py            # Facial asymmetry detection
│       ├── hand_face_touch_module.py      # Self-adaptor gesture detection
│       ├── nlp_deception_module.py        # Groq LLM text analysis
│       ├── fusion_engine.py               # Multi-modal score fusion + verdict
│       └── reasoning_engine.py            # Natural language explanation
├── frontend/
│   ├── main.py                            # Desktop app entry (Eel)
│   ├── web_app.py                         # Web-mode launcher
│   ├── config.py                          # Backend URL configuration
│   ├── requirements.txt                   # eel, tinydb, requests
│   ├── pyproject.toml
│   ├── RUN.bat                            # Windows quick-launch script
│   ├── main.spec                          # PyInstaller spec (frontend)
│   ├── README.md
│   └── web/
│       ├── index.html
│       ├── pages/
│       │   ├── login.html                 # User authentication
│       │   ├── signup.html                # User registration
│       │   ├── dashboard.html             # Analytics hub & trend charts
│       │   ├── start-session.html         # Live recording & analysis
│       │   ├── uploads.html               # Evidence vault management
│       │   ├── reports.html               # Case report listing
│       │   ├── report-detail.html         # Single report deep-dive
│       │   ├── profile.html               # User profile editor
│       │   ├── settings.html              # Application settings
│       │   └── voice-analysis.html        # Voice-only analysis view
│       ├── js/
│       │   ├── common/                    # Shared utilities (api.js, auth.js, utils.js)
│       │   ├── components/                # Reusable UI (sidebar.js, loader.js)
│       │   └── pages/                     # Page-specific logic
│       ├── styles/output.css              # Compiled application stylesheet
│       ├── scripts/                       # chart.min.js, wavesurfer.min.js
│       └── assets/images/                 # Logos and brand assets
└── frontend/modules/
    └── database.py                        # TinyDB CRUD operations
```

---

## API Reference (FastAPI Backend)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server status and registered modules |
| `/analyze/voice` | GET / POST | Forensic voice stress & transcriptional analysis |
| `/analyze/emotion` | GET / POST | Facial emotion detection |
| `/analyze/face/gaze` | GET / POST | Eye gaze tracking & blink analysis |
| `/analyze/face/pose` | GET / POST | Head pose estimation & gesture detection |
| `/analyze/face/lipjaw` | GET / POST | Lip / jaw tension scoring |
| `/analyze/face/asymmetry` | GET / POST | Facial asymmetry detection |
| `/analyze/face/touch` | GET / POST | Hand-to-face touch detection |
| `/analyze/face/emotion` | GET / POST | Full-frame facial emotion analysis |
| `/analyze/face` | GET / POST | Parallel full-face analysis (all modules) |
| `/analyze/pipeline` | GET / POST | End-to-end deception detection pipeline |

Interactive API documentation available at `http://localhost:8000/docs` when the backend server is running.

---

## Quick Start

### Prerequisites
- Python 3.9 or newer
- FFmpeg (required for audio extraction and video processing; must be in system PATH)
- Windows, macOS, or Linux

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here
```

Start the backend server:

```bash
python server.py
# Server runs at http://localhost:8000
```

### 2. Frontend Setup

```bash
cd frontend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Launch the desktop application:

```bash
python main.py
```

Alternatively, for a web-mode launch:

```bash
python web_app.py
```

### 3. Quick Launch (Windows)

Run the included batch script from the `frontend/` directory:

```bash
RUN.bat
```

---

## Key Design Decisions

- **Offline-First Models** — Whisper and PyAnnote models can be pre-downloaded via `download_models.py` for environments without internet access.
- **PyInstaller Compatible** — Both backend and frontend include `.spec` files for desktop executable packaging.
- **No Central Auth Server** — Authentication is handled locally via TinyDB for portability and simplicity in a research context.
- **100% Offline Diarization** — PyAnnote pipeline runs from a local `config.yaml` without requiring HuggingFace runtime access at inference time.
- **Bilingual by Design** — NLP analysis natively supports English and Roman Urdu with automatic translation.

---

## Research Context

Deceptron was developed as a Final Year Project (FYP) by **Ali Hamza** to explore multi-modal deception detection in forensic interview scenarios. The system integrates computer vision, audio forensics, and computational linguistics into a single interpretable scoring framework.

---

## Related Documentation

- `backend/README.md` — Detailed backend module setup and behavior
- `frontend/README.md` — Frontend installation, Eel configuration, and UI architecture
- `backend/modules/*.py` — Source-level documentation and class definitions

---

## License

This is a research/educational project developed for academic submission. Please refer to individual module documentation for third-party license information (PyTorch, MediaPipe, Whisper, PyAnnote, HSEmotion, Groq).
