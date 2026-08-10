# Deceptron Frontend

Desktop interface for the Deceptron deception detection system. It connects to
the FastAPI backend for analysis and stores user data locally with TinyDB.

**Version:** 1.4.0
**Project:** Final Year Project (FYP)
**Stack:** Python + Eel (desktop bridge), Vanilla JavaScript, HTML5, CSS

---

## Overview

Deceptron is a desktop application for analyzing behavioral cues from video
and audio interviews. The frontend handles login/signup, live session
recording, media uploads, report viewing, and profile settings. All analysis
is done by the backend and shown here in a clean interface.

---

## Features

### Live Session
- Records video/audio from the camera and microphone.
- Uploads recordings in 1MB chunks to avoid memory issues.
- Shows a live preview before analysis starts.

### Facial Micro-Expressions
- Dedicated module for subtle facial changes.
- Unmirrored playback view for reviewing evidence.
- Tabbed results for 6 face analysis types: Emotion, Eyes, Lip/Jaw, Head,
  Asymmetry, Touch. Table IDs are kept for backward compatibility.

### Voice Analysis
- Frequency stability and acoustic jitter indicators.
- Emotion cards with color coding.
- Interactive zoomable waveform using WaveSurfer.js.

### NLP Deception Analysis
- Color-coded flags: evasion/contradiction (rose),
  cognitive_load/distancing_language (purple), vagueness/over_explanation
  (amber).
- Toggle between English and Roman Urdu summaries.
- Uses Groq-hosted Llama-3.3-70B for text analysis.

### Fusion Breakdown
- 5 weighted bars: Face Behavioral, Face Emotion, Voice Stress, NLP
  Deception, Mismatch.
- Warning/info flags for conflicts between modules.
- Verdict badge with English/Urdu toggle.

### Reports & Media
- Auto-generated case reports with trend charts.
- Media is stored under `~/.deceptron/recordings/`.
- Search for cases by analyst, ID, or subject name.

---

## Tech Stack

### Frontend
- **Bridge**: Eel (Python-JS) over a Bottle server.
- **Logic**: Plain ES6 JavaScript, no heavy frameworks.
- **Styling**: Custom CSS with HSL-based glow effects. Fonts: Orbitron
  (headings) and Inter (body). Layout uses Grid and Flexbox.

### Backend / Storage
- **Database**: TinyDB, stored in `~/.deceptron` so it survives restarts.
- **Runtime**: Python 3.9+ with the gevent event loop.

---

## Installation & Setup

### Requirements
- **Python 3.9**
- **Chrome/Edge** (used for the application window)
- **Camera/Mic** (physical devices; virtual drivers are filtered out)

### 1. Manual Installation (pip)
```bash
git clone https://github.com/AliHamza-Coder/Deceptron-Fyp-Final-Year-Project.git
cd Deceptron-Fyp-Final-Year-Project

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

### 2. Quick Run (Windows)
Double-click **`RUN.bat`** to set up the environment and launch the app.

---

## Building the Executable

To create a standalone version:

### Using PyInstaller
```bash
pip install pyinstaller
pyinstaller main.spec
```

The executable will be in the `dist/` directory as `deceptron.exe`.

---

## Project Details
- **Project title**: Deceptron — Deception Detection System
- **Project lead**: Ali Hamza
- **Type**: Final Year Project (FYP)
- **Version**: 1.4.0
