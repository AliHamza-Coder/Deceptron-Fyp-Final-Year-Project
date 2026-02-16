# DECEPTRON - Advanced Truth Verification System

<div align="center">

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**A cutting-edge AI-powered desktop application for real-time emotion detection and behavioral analysis**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Requirements](#-system-requirements)
- [Installation Guide](#-installation-guide)
- [Quick Start](#-quick-start)
- [User Guide](#-user-guide)
- [Technical Architecture](#-technical-architecture)
- [Troubleshooting](#-troubleshooting)
- [Developer Information](#-developer-information)

---

## 🎯 Overview

DECEPTRON is a professional-grade hybrid desktop application that combines advanced AI/ML algorithms with an intuitive user interface for real-time emotion detection and behavioral analysis. Built with Python for robust backend processing and modern web technologies for a responsive frontend experience.

### Use Cases

- **Security & Investigation**: Real-time interview analysis
- **Research**: Behavioral pattern studies
- **Training**: Communication skills assessment
- **Media Analysis**: Pre-recorded content evaluation

---

## ✨ Key Features

### Core Capabilities

- 🎥 **Real-time Facial Expression Analysis** - Detect 8 emotions with confidence scores (HSEmotion)
- 🎙️ **Voice Stress Detection** - Analyze vocal patterns for stress indicators (New in v1.1.0)
- 📊 **Live Dashboard** - Comprehensive real-time analytics and visualizations
- 📁 **File Processing** - Analyze pre-recorded video/audio files
- 📝 **Detailed Reports** - Generate professional analysis reports
- 🎨 **Dual Theme Support** - Light and Dark modes for comfortable viewing
- 🔒 **Secure Vault** - Encrypted evidence storage and management
- 🛠️ **Smart Device Management** - Auto-detects real hardware, filters virtual devices

### Technical Highlights

- **AI Models**: HSEmotion (EfficientNet-based emotion recognition)
- **Face Detection**: MediaPipe (Google's ML solution)
- **Real-time Processing**: High-performance detection with minimal latency
- **Chunked Data Transfer**: Optimized saving for large video/audio files (New in v1.1.0)
- **Cross-platform**: Windows, macOS, Linux support

---

## 💻 System Requirements

### Minimum Requirements

- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.9 (recommended)
- **RAM**: 4 GB
- **Storage**: 2 GB free space
- **Camera**: USB/built-in webcam (720p minimum)
- **Microphone**: Standard audio input device
- **Browser**: Chrome 90+, Edge 90+, or Firefox 88+

### Recommended Requirements

- **Python**: 3.9
- **RAM**: 8 GB or higher
- **GPU**: NVIDIA GPU with CUDA support (for faster processing)
- **Camera**: 1080p webcam for optimal accuracy
- **Internet**: Required for initial model downloads

---

## 📦 Installation Guide

### Step 1: Install Python

1. Download Python 3.9 from [python.org](https://www.python.org/downloads/release/python-390/)
2. During installation, **check "Add Python to PATH"**
3. Verify installation:
   ```bash
   python --version
   ```
   Should display: `Python 3.9.x`

### Step 2: Clone/Download Project

```bash
git clone https://github.com/AliHamza-Coder/Deceptron-Fyp-Final-Year-Project.git
cd Deceptron-Fyp-Final-Year-Project
cd "DEceptron Screens/Frontend"
```

Or download ZIP from [GitHub Repository](https://github.com/AliHamza-Coder/Deceptron-Fyp-Final-Year-Project) and extract.

### Step 3: Create Virtual Environment

**Windows:**

```bash
python -m venv myenv
myenv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv myenv
source myenv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: First run will download AI models (~200MB). Ensure stable internet connection.

### Step 5: Verify Installation

```bash
python main.py
```

If successful, the application window will open automatically.

---

## 🚀 Quick Start

### Windows Users (Easiest Method)

1. Double-click `RUN.bat` in the project folder
2. Wait for the application to launch
3. Grant camera/microphone permissions when prompted

### Manual Launch

1. Open terminal/command prompt
2. Navigate to project directory
3. Activate virtual environment:
   ```bash
   myenv\Scripts\activate  # Windows
   source myenv/bin/activate  # macOS/Linux
   ```
4. Run application:
   ```bash
   python main.py
   ```

---

## 📖 User Guide

### First Time Setup

1. **Launch Application** - Use `RUN.bat` or `python main.py`
2. **Login/Signup** - Create a secure account to access the dashboard
3. **Grant Permissions** - Allow camera and microphone access
4. **Navigate Interface** - Explore the dashboard overview

### Using Live Session Mode

1. **Navigate**: Click "Live Session" from sidebar
2. **Setup Devices**: Select your preferred **Camera** and **Microphone** from the right sidebar. _Virtual devices are automatically filtered._
3. **Start Camera**: Click "Turn on Camera" button
4. **Record Session**: Click "Start Recording" to capture video & audio
5. **End Session**: Click "Stop Recording" and name your session. Wait for the "Encrypting & Saving to Vault..." loader to finish.

### Using Facial Expression Analysis

1. **Navigate**: Click "Facial Micro-Exp" from sidebar
2. **Choose Source**:
   - **Live Camera**: Click "Initiate Deep Scanner"
   - **File Upload**: Click "Load File" and select video
3. **View Analysis**: Monitor emotion radar and micro-expression metrics
4. **Adjust Settings**: Toggle detection modules in right panel

### Using Voice Analysis (New)

1. **Navigate**: Click "Voice Analysis" to access vocal stress metrics.
2. **Record/Load**: Record live audio or load a session from the Vault.
3. **Analyze**: View stress indicators, pitch analysis, and speech patterns.

### Analyzing Evidence (Vault)

1. Click "Evidence Vault" or use the "Load from Vault" button in any analysis page.
2. Browse securely stored recordings (Video sessions, Voice logs).
3. Click any file to load it directly into the analysis pipeline.

### Understanding Results

#### Emotion Detection

- **8 Emotions Tracked**: Anger, Contempt, Disgust, Fear, Happiness, Neutral, Sadness, Surprise
- **Confidence Score**: 0-100% accuracy indicator
- **Color Coding**:
  - 🔵 Cyan = Neutral/Calm
  - 🔴 Red = Negative emotions
  - 🟡 Amber = Stress/Fear
  - 🟢 Green = Positive emotions

#### Bounding Box

- **Cyan Box**: Face detection area
- **Label**: Current emotion with confidence percentage
- **Real-time Updates**: Refreshes every 500ms

### Tips for Best Results

✅ **DO:**

- Use good lighting (face clearly visible)
- Position face 2-3 feet from camera
- Keep face centered in frame
- Minimize background movement
- Use stable internet for first run

❌ **DON'T:**

- Cover face with hands/objects
- Use in very dark environments
- Move too quickly or erratically
- Use low-quality cameras (<480p)

---

## 🔧 Troubleshooting

### Camera/Mic Not Detected

**Problem**: "No Camera Detected" or dropdown is empty.

**Solutions**:

1. Check browser/system permissions.
2. Ensure you are using a **physical device** (virtual cameras/mics are filtered out).
3. Restart the application (`python main.py`) to refresh device list.

### Recording Save Failed

**Problem**: Updates stick at "Saving... 0%" or error toast appears.

**Solutions**:

1. Ensure you have sufficient disk space.
2. Wait for the **Chunked Upload** process to finish (do not close the app while saving).
3. Check `main.py` console output for specific error codes.

### Model Loading Errors

**Problem**: "Failed to load model" or "WeightsUnpickler" error.

**Solutions**:

1. Ensure stable internet connection.
2. Delete and reinstall dependencies:
   ```bash
   pip uninstall hsemotion torch
   pip install -r requirements.txt
   ```
3. Check Python version (must be 3.9).
4. Try running as administrator.

### Application Won't Start

**Problem**: Window doesn't open or crashes immediately.

**Solutions**:

1. Verify Python installation: `python --version` (should be 3.9).
2. Activate virtual environment.
3. Reinstall dependencies: `pip install -r requirements.txt`.
4. Check console for error messages.
5. Ensure port 8000 is not in use.

---

## 👨‍💻 Developer Information

### For Developers

#### Adding New Features

**Camera/Video Processing**:

- Frontend: Use `navigator.mediaDevices.getUserMedia()` for display
- Backend: Process frames in Python with OpenCV
- Communication: Use `eel.expose` decorator for Python functions

**Example**:

```python
@eel.expose
def process_frame(base64_image):
    frame = decode_base64_to_frame(base64_image)
    result = analyze_frame(frame)
    return result
```

#### Code Style

- Python: PEP 8 guidelines
- JavaScript: ES6+ standards
- Comments: Docstrings for all functions

#### Testing

```bash
python modules/emotion_functions.py  # Test emotion module
python modules/camera_functions.py   # Test camera module
```

### Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch
3. Commit changes with clear messages
4. Submit pull request

### License

MIT License - See LICENSE file for details

### Support

For issues or questions:

- 📧 Email: support@deceptron.ai
- 🐛 Issues: GitHub Issues page
- 📚 Docs: [Documentation Portal]

---

## 📝 Version History

### v1.1.0 (Current)

- ✅ **New**: Voice Stress Analysis Module
- ✅ **New**: Smart Device Detection (Auto-filters virtual hardware)
- ✅ **New**: Chunked Upload System (Optimized for large recordings)
- ✅ **New**: Secure Vault System for Evidence Management
- ✅ **Improved**: Login/Signup Flow with Visual Feedback
- ✅ **Improved**: Live Session UI and UX

### v1.0.0

- ✅ Real-time emotion detection
- ✅ Facial expression analysis module
- ✅ Live session recording
- ✅ File upload and processing
- ✅ Light/Dark theme support
- ✅ Professional reporting system
- ✅ Camera flip fix for accurate detection

### Upcoming Features

- 🔜 Multi-face detection support
- 🔜 Advanced report customization
- 🔜 Cloud storage integration
- 🔜 Mobile app companion

---

<div align="center">

**Developed with ❤️ by Ali Hamza-Coder**

_Empowering truth through technology_

</div>
