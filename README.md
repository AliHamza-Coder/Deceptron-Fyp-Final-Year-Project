# Deceptron — Multi-Modal Deception Detection System

**Version:** 1.4.0  
**Lead Developer:** Ali Hamza  
**Type:** Final Year Project (FYP) — Desktop Application  
**Status:** Research / educational use

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![UI](https://img.shields.io/badge/UI-Eel%20%2B%20JavaScript-F7DF1E)
![License](https://img.shields.io/badge/License-Academic-yellow)

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [How the Pipeline Works](#how-the-pipeline-works)
5. [Project Structure](#project-structure)
6. [Tech Stack](#tech-stack)
7. [API Reference](#api-reference)
8. [Accuracy](#accuracy)
9. [Quick Start](#quick-start)
10. [Key Design Decisions](#key-design-decisions)
11. [Limitations & Future Work](#limitations--future-work)
12. [Research Context](#research-context)
13. [Related Documentation](#related-documentation)
14. [License](#license)

---

## Overview

Deceptron is a deception detection system that combines three types of behavioral analysis — facial micro-expressions, vocal stress patterns, and linguistic indicators — into a single score. It processes live or pre-recorded video/audio interviews through a modular pipeline of AI/ML components and shows the results in a desktop interface.

The system is meant for investigative and research use. It compares a person's behavior against a baseline, identifies who is speaking, and checks for conflicts between what the face, voice, and words are saying.

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
Groq-hosted Llama-3.3-70B-Versatile analyzes spoken transcripts for 8 linguistics indicators:
- **Evasion** — non-answers, topic changes
- **Over-explanation** — unnecessary specificity
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
The core decision layer combines all modalities using weighted rules:

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
- Doughnut chart showing High-Risk / Trustworthy case distribution (deception scores above 50 vs at/below 50)
- Recent analysis history table with color-coded risk indicators
- Case count counter and per-report risk score calculation
- Real-time data refresh via TinyDB queries

### 13. User Account System
- Secure registration and login (SHA-256 + salt)
- Email verification and password reset (SMTP)
- Profile management with avatar support
- Session persistence across application restarts

### 14. Profile & Settings Management
- Editable user profile (name, username, avatar)
- Settings page for camera/mic selection and video appearance

---

## System Architecture

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

## How the Pipeline Works

A single pipeline run looks like this:

```
video file
   │  FFmpeg audio extraction
   ▼
speaker diarization (PyAnnote — identifies the suspect)
   │
   ▼
question-answer segmentation (Whisper transcription + VAD splitting)
   │
   ▼
per segment (run in parallel):
   │  • 6 face modules (gaze, pose, lip-jaw, asymmetry, touch, emotion)
   │  • voice stress analysis (jitter, shimmer, HNR, F0, pauses)
   │  • NLP deception analysis (Groq Llama-3.3-70B on the transcript)
   ▼
fusion engine (weighted 35/10/25/25/5 + bonus rules + conflict/spike checks)
   │
   ▼
deception score + confidence + bilingual reasoning (English / Roman Urdu)
   │
   ▼
report saved to TinyDB  +  annotated / 2×2 combined output video
```

---

## Project Structure

```
Deceptron-Fyp-Final-Year-Project/
├── README.md
├── FYP_STUDY_GUIDE.md              # Viva/prep Q&A for the developer
├── PRESENTATION_PREP.md            # Demo flow + examiner questions (private)
├── SYSTEM_ACCURACY_EXPLANATION.md  # How the accuracy estimate was derived
├── calculate_system_accuracy.py    # Accuracy estimation script
├── .gitignore
│
├── backend/
│   ├── server.py                          # FastAPI entry point & route registration
│   ├── requirements.txt                   # Python dependencies
│   ├── .env.example                       # GROQ_API_KEY template (real .env is gitignored)
│   ├── download_models.py                 # Offline model downloader
│   ├── build_backend.ps1 / deceptron_backend.spec   # PyInstaller packaging
│   ├── api/
│   │   └── routes/
│   │       ├── voice.py                   # /analyze/voice
│   │       ├── emotion.py                 # /analyze/emotion
│   │       ├── face.py                    # /analyze/face/* (6 sub-routes + parallel)
│   │       └── pipeline.py                # /analyze/pipeline (end-to-end)
│   ├── modules/
│   │   ├── main.py                        # Pipeline CLI entry (testing)
│   │   ├── speaker_diarizer.py            # PyAnnote speaker identification
│   │   ├── segment_manager.py             # Q&A segmentation + VAD
│   │   ├── forensic_voice_analyzer.py     # Praat acoustics + Whisper transcription
│   │   ├── emotion_detection_module.py    # HSEmotion realtime classification
│   │   ├── eye_gaze_module.py             # MediaPipe gaze / blink tracking
│   │   ├── head_pose_module.py            # Head pose angles & gestures
│   │   ├── lip_jaw_module.py              # Lip/jaw tension analysis
│   │   ├── asymmetry_module.py            # Facial asymmetry detection
│   │   ├── hand_face_touch_module.py      # Self-adaptor gesture detection
│   │   ├── nlp_deception_module.py        # Groq LLM text analysis
│   │   ├── fusion_engine.py               # Multi-modal score fusion + verdict
│   │   └── reasoning_engine.py            # Bilingual natural-language explanation
│   └── local_models/                      # Downloaded model weights (offline inference)
│
└── frontend/
    ├── main.py                            # Desktop app entry (Eel)
    ├── web_app.py                         # Web-mode launcher
    ├── config.py                          # Backend URL + SMTP configuration
    ├── requirements.txt / pyproject.toml
    ├── RUN.bat                            # Windows quick-launch script
    ├── main.spec                          # PyInstaller spec (frontend)
    ├── modules/
    │   ├── database.py                    # TinyDB CRUD operations
    │   ├── email_sender.py                # SMTP email sending
    │   └── email_templates/               # HTML email templates
    └── web/
        ├── index.html
        ├── pages/                         # login, signup, dashboard, start-session,
        │                                  # facial-expression, voice-analysis, uploads,
        │                                  # reports, report-detail, profile, settings ...
        ├── js/
        │   ├── common/                    # api.js, auth.js, utils.js, constants.js ...
        │   ├── components/                # sidebar.js, loader.js, vault-component.js ...
        │   └── pages/                     # page-specific scripts
        ├── styles/output.css              # Compiled application stylesheet
        ├── scripts/                       # chart.min.js, wavesurfer.min.js
        └── assets/images/                 # Logos and brand assets
```

---

## Tech Stack

### Backend — AI / ML Pipeline
| Component | Technology |
|-----------|-----------|
| Server Framework | FastAPI (Python 3.9+) |
| Deep Learning | PyTorch, TorchVision |
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
| Styling | Custom CSS (CSS Variables) |
| Charts | Chart.js |
| Audio Visualization | WaveSurfer.js |
| Icons | Font Awesome |
| Database | TinyDB (local JSON storage) |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Authentication | SHA-256 + Salt hashing, session-managed |
| Email | SMTP (verification + password reset) |
| Persistence | TinyDB (`~/.deceptron/db.json`) |
| File Storage | `~/.deceptron/results/`, `~/.deceptron/reports/` |
| Build / Packaging | PyInstaller (desktop executable support) |

---

## API Reference

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

Interactive API documentation is available at `http://localhost:8000/docs` when the backend server is running.

---

## Accuracy

The project ships with an **estimated** system accuracy of **89.1%**. This number is not the result of testing on a labelled deception dataset — it is computed by `calculate_system_accuracy.py`, which averages published benchmark accuracies of the individual components (emotion model, diarization, transcription, etc.), weighted by the same weights used in the fusion engine (35/10/25/25/5).

See [SYSTEM_ACCURACY_EXPLANATION.md](SYSTEM_ACCURACY_EXPLANATION.md) for the full methodology. Validation on public deception datasets (e.g. RLDD, Miami Deception Dataset) is planned future work.

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

Create a `.env` file in the `backend/` directory (copy the template):

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

Optionally create a `frontend/.env` file for email features (verification / password reset):

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
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

### 4. Downloading Models Offline (Optional)

If the machine has no internet at runtime, pre-download Whisper and PyAnnote models:

```bash
cd backend
python download_models.py
```

---

## Key Design Decisions

- **Offline-First Models** — Whisper and PyAnnote models can be pre-downloaded via `download_models.py` for environments without internet access.
- **PyInstaller Compatible** — Both backend and frontend include `.spec` files for desktop executable packaging.
- **No Central Auth Server** — Authentication is handled locally via TinyDB for portability and simplicity in a research context.
- **100% Offline Diarization** — PyAnnote pipeline runs from a local `config.yaml` without requiring HuggingFace runtime access at inference time.
- **Bilingual by Design** — NLP analysis natively supports English and Roman Urdu with automatic translation.
- **Personalized Baseline** — The first 10 seconds of a session become the subject's own "normal behavior" baseline, so the analysis is per-person, not one-size-fits-all.

---

## Limitations & Future Work

**Limitations:**
- The 89.1% figure is an estimate from component benchmarks, not a measured result on a deception dataset.
- The NLP module requires an internet connection (Groq API).
- Baseline quality depends on the first 10 seconds of a session being "normal" behavior.
- Results are best with good lighting, clear audio, and an unobstructed face.
- Deception detection science is contested; the system is an assistive cue-flagging tool, not a definitive lie detector.

**Future Work:**
- Validation on public deception datasets (RLDD, Miami Deception Dataset).
- Optional local LLM so NLP runs fully offline.
- Real-time continuous analysis instead of post-session processing.
- Measuring and tuning the fusion weights from actual data instead of rule-based choices.

---

## Research Context

Deceptron was developed as a Final Year Project (FYP) by **Ali Hamza** to explore multi-modal deception detection in forensic interview scenarios. The system integrates computer vision, audio forensics, and computational linguistics into a single interpretable scoring framework.

---

## Related Documentation

- [`FYP_STUDY_GUIDE.md`](FYP_STUDY_GUIDE.md) — page-wise, folder-wise and module-wise Q&A for understanding the project.
- [`PRESENTATION_PREP.md`](PRESENTATION_PREP.md) — demo flow and examiner-question preparation.
- [`SYSTEM_ACCURACY_EXPLANATION.md`](SYSTEM_ACCURACY_EXPLANATION.md) — accuracy methodology.
- `backend/README.md` — detailed backend module setup and behavior.
- `frontend/README.md` — frontend installation, Eel configuration, and UI architecture.
- `backend/modules/*.py` — source-level documentation and class definitions.

---

## License

This is a research/educational project developed for academic submission. Refer to the individual module documentation for third-party license information (PyTorch, MediaPipe, Whisper, PyAnnote, HSEmotion, Groq).
