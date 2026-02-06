# DECEPTRON - Advanced Truth Verification System

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
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
- 🎥 **Real-time Facial Expression Analysis** - Detect 8 emotions with confidence scores
- 🎤 **Voice Stress Detection** - Analyze vocal patterns for stress indicators
- 📊 **Live Dashboard** - Comprehensive real-time analytics and visualizations
- 📁 **File Processing** - Analyze pre-recorded video/audio files
- 📝 **Detailed Reports** - Generate professional analysis reports
- 🎨 **Dual Theme Support** - Light and Dark modes for comfortable viewing
- 🔒 **Secure Sessions** - Encrypted data storage and session management

### Technical Highlights
- **AI Models**: HSEmotion (EfficientNet-based emotion recognition)
- **Face Detection**: MediaPipe (Google's ML solution)
- **Real-time Processing**: 2 FPS emotion detection with minimal latency
- **Cross-platform**: Windows, macOS, Linux support

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.9 (recommended)
- **RAM**: 4 GB
- **Storage**: 2 GB free space
- **Camera**: Any USB/built-in webcam (720p minimum)
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
2. **Grant Permissions** - Allow camera and microphone access
3. **Navigate Interface** - Explore the welcome screen and dashboard

### Using Live Session Mode

1. **Navigate**: Click "Live Session" from sidebar
2. **Start Camera**: Click "Turn on Camera" button
3. **Position Face**: Ensure face is clearly visible and well-lit
4. **View Results**: Real-time emotion detection appears on screen
5. **Record Session**: Click "Start Recording" to save analysis
6. **End Session**: Click "End Session" and save/discard data

### Using Facial Expression Analysis

1. **Navigate**: Click "Facial Micro-Exp" from sidebar
2. **Choose Source**:
   - **Live Camera**: Click "Initiate Deep Scanner"
   - **File Upload**: Click "Load File" and select video
3. **View Analysis**: Monitor emotion radar and micro-expression metrics
4. **Adjust Settings**: Toggle detection modules in right panel

### Analyzing Pre-recorded Files

1. Click "Load from Vault" or "Evidence Vault"
2. Select video/audio file from list
3. Wait for processing to complete
4. Review detailed analysis results
5. Export report if needed

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

## 🏗️ Technical Architecture

### System Design

```
┌─────────────────────────────────────────┐
│          Frontend (Web UI)              │
│  HTML5 + CSS3 + JavaScript + Chart.js   │
└──────────────┬──────────────────────────┘
               │ Eel Bridge (WebSocket)
┌──────────────▼──────────────────────────┐
│         Backend (Python)                │
│  • Emotion Detection (HSEmotion)        │
│  • Face Detection (MediaPipe)           │
│  • Frame Processing (OpenCV)            │
│  • Data Management                      │
└─────────────────────────────────────────┘
```

### Data Flow

1. **Capture**: JavaScript captures video frame from webcam
2. **Encode**: Frame converted to base64 JPEG
3. **Transfer**: Sent to Python via Eel bridge
4. **Process**: Python decodes, flips, detects face, analyzes emotion
5. **Return**: Results sent back to JavaScript
6. **Display**: UI updates with bounding box and emotion label

### Project Structure

```
DEceptron Screens/Frontend/
├── main.py                    # Application entry point
├── RUN.bat                    # Windows launcher
├── README.md                  # Documentation
├── modules/                   # Python modules
│   ├── camera_functions.py    # Camera operations
│   ├── emotion_functions.py   # Emotion detection
│   └── device_functions.py    # Device management
├── web/                       # Frontend assets
│   ├── pages/                 # HTML pages
│   │   ├── welcome.html       # Landing page
│   │   ├── dashboard.html     # Main dashboard
│   │   ├── live-session.html  # Live analysis
│   │   ├── facial-expression.html  # Facial module
│   │   └── ...                # Other pages
│   ├── scripts/               # JavaScript files
│   ├── styles/                # CSS stylesheets
│   └── assets/                # Images, icons, fonts
└── myenv/                     # Virtual environment
```

### Key Technologies

- **Eel**: Python-JavaScript bridge
- **HSEmotion**: State-of-the-art emotion recognition
- **MediaPipe**: Efficient face detection
- **OpenCV**: Image processing
- **PyTorch**: Deep learning framework
- **Chart.js**: Data visualization

---

## 🔧 Troubleshooting

### Camera Not Working

**Problem**: "Could not access camera" error

**Solutions**:
1. Check browser permissions (allow camera access)
2. Close other apps using camera (Zoom, Skype, etc.)
3. Try different camera from dropdown
4. Restart application
5. Check camera drivers are updated

### Slow Performance

**Problem**: Laggy or delayed detection

**Solutions**:
1. Close unnecessary applications
2. Reduce video quality in settings
3. Ensure adequate lighting (reduces processing)
4. Update GPU drivers (if using CUDA)
5. Check CPU usage in Task Manager

### Model Loading Errors

**Problem**: "Failed to load model" or "WeightsUnpickler" error

**Solutions**:
1. Ensure stable internet connection
2. Delete and reinstall dependencies:
   ```bash
   pip uninstall hsemotion torch
   pip install -r requirements.txt
   ```
3. Check Python version (must be 3.9)
4. Try running as administrator

### Application Won't Start

**Problem**: Window doesn't open or crashes immediately

**Solutions**:
1. Verify Python installation: `python --version` (should be 3.9)
2. Activate virtual environment
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Check console for error messages
5. Ensure port 8000 is not in use

### Face Not Detected

**Problem**: "No Face Detected" message persists

**Solutions**:
1. Improve lighting conditions
2. Move closer to camera (2-3 feet optimal)
3. Center face in frame
4. Remove obstructions (glasses, masks may affect accuracy)
5. Ensure camera is focused

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

### v1.0.0 (Current)
- ✅ Real-time emotion detection
- ✅ Facial expression analysis module
- ✅ Live session recording
- ✅ File upload and processing
- ✅ Light/Dark theme support
- ✅ Professional reporting system
- ✅ Camera flip fix for accurate detection

### Upcoming Features
- 🔜 Voice stress analysis integration
- 🔜 Multi-face detection support
- 🔜 Advanced report customization
- 🔜 Cloud storage integration
- 🔜 Mobile app companion

---

<div align="center">

**Developed with ❤️ by Ali Hamza-Coder**

*Empowering truth through technology*

</div>
