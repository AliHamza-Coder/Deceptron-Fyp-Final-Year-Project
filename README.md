# DECEPTRON - Advanced Truth Verification System

<div align="center">

![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**A cutting-edge AI-powered desktop application for behavioral analysis and evidence management**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Requirements](#-system-requirements)
- [Installation Guide](#-installation-guide)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [User Guide](#-user-guide)
- [Troubleshooting](#-troubleshooting)
- [Developer Information](#-developer-information)

---

## 🎯 Overview

DECEPTRON is a professional-grade hybrid desktop application combining Python backend processing with modern web technologies for a responsive frontend experience. Designed for security professionals, researchers, and analysts.

### Use Cases

- **Security & Investigation**: Real-time interview analysis
- **Research**: Behavioral pattern studies
- **Training**: Communication skills assessment
- **Media Analysis**: Pre-recorded content evaluation

---

## ✨ Key Features

### Core Capabilities

- 🎥 **Live Session Recording** - High-quality video/audio capture
- 🎙️ **Voice Analysis** - Vocal pattern analysis
- 📊 **Live Dashboard** - Comprehensive real-time analytics
- 📁 **File Processing** - Analyze pre-recorded media files
- 📝 **Detailed Reports** - Professional analysis reports
- 🎨 **Dual Theme Support** - Light and Dark modes
- 🔒 **Secure Vault** - Encrypted evidence storage
- 🛠️ **Smart Device Management** - Auto-detects real hardware

### Technical Highlights

- **Real-time Processing**: High-performance with minimal latency
- **Chunked Data Transfer**: Optimized for large files (v1.2.0)
- **Modular Architecture**: Clean separation of concerns (v1.2.0)
- **Cross-platform**: Windows, macOS, Linux support

---

## 💻 System Requirements

### Minimum Requirements

- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.9 (required)
- **RAM**: 4 GB
- **Storage**: 2 GB free space
- **Camera**: USB/built-in webcam (720p minimum)
- **Microphone**: Standard audio input device
- **Browser**: Chrome 90+, Edge 90+, or Firefox 88+

### Recommended Requirements

- **Python**: 3.9
- **RAM**: 8 GB or higher
- **Camera**: 1080p webcam for optimal quality
- **Internet**: Required for initial setup

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
myenv\\Scripts\\activate
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
   myenv\\Scripts\\activate  # Windows
   source myenv/bin/activate  # macOS/Linux
   ```
4. Run application:
   ```bash
   python main.py
   ```

---

## 📁 Project Structure

```
Frontend/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── RUN.bat                # Windows launcher
├── db.json                # User database
│
├── modules/               # Backend modules
│   └── database.py        # Database operations
│
└── web/                   # Frontend files
    ├── assets/            # Images, fonts, icons
    │   ├── images/
    │   └── fonts/
    │
    ├── css/               # Stylesheets
    │   └── spa-shell.css
    │
    ├── js/                # JavaScript modules
    │   ├── common/        # Shared utilities
    │   │   ├── utils.js       # Helper functions
    │   │   ├── api.js         # EEL API wrappers
    │   │   ├── auth.js        # Session management
    │   │   └── constants.js   # App constants
    │   │
    │   ├── components/    # Reusable components
    │   │   ├── loader.js
    │   │   ├── sidebar.js
    │   │   ├── vault-component.js
    │   │   └── media-preview.js
    │   │
    │   └── pages/         # Page-specific logic
    │       └── (page scripts)
    │
    ├── pages/             # HTML pages
    │   ├── login.html
    │   ├── signup.html
    │   ├── dashboard.html
    │   ├── live-session.html
    │   ├── voice-analysis.html
    │   ├── facial-expression.html
    │   ├── uploads.html
    │   ├── settings.html
    │   └── profile.html
    │
    ├── uploads/           # User uploaded files
    └── recordings/        # Session recordings
```

---

## 📖 User Guide

### First Time Setup

1. **Launch Application** - Use `RUN.bat` or `python main.py`
2. **Login/Signup** - Create a secure account
3. **Grant Permissions** - Allow camera and microphone access
4. **Navigate Interface** - Explore the dashboard

### Using Live Session Mode

1. **Navigate**: Click "Live Session" from sidebar
2. **Setup Devices**: Select Camera and Microphone
3. **Start Camera**: Click "Turn on Camera" button
4. **Record Session**: Click "Start Recording"
5. **End Session**: Click "Stop Recording" and name your session

### Using Voice Analysis

1. **Navigate**: Click "Voice Analysis"
2. **Record/Load**: Record live or load from Vault
3. **Analyze**: View stress indicators and patterns

### Evidence Vault

1. Click "Evidence Vault" button
2. Browse securely stored recordings
3. Click any file to load into analysis

### Tips for Best Results

✅ **DO:**

- Use good lighting
- Position face 2-3 feet from camera
- Keep face centered in frame
- Minimize background movement

❌ **DON'T:**

- Cover face with objects
- Use in very dark environments
- Move too quickly
- Use low-quality cameras (<480p)

---

## 🔧 Troubleshooting

### Camera/Mic Not Detected

**Solutions**:

1. Check browser/system permissions
2. Ensure using **physical device** (virtual devices filtered)
3. Restart application

### Recording Save Failed

**Solutions**:

1. Ensure sufficient disk space
2. Wait for upload process to finish
3. Check console for error messages

### Application Won't Start

**Solutions**:

1. Verify Python 3.9: `python --version`
2. Activate virtual environment
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Ensure port 8000 is available

---

## 👨‍💻 Developer Information

### Architecture

**Backend (Python)**:

- `main.py` - Eel application server
- `modules/database.py` - TinyDB operations
- EEL exposed functions for frontend communication

**Frontend (Web)**:

- HTML5 for structure
- Vanilla CSS for styling
- Vanilla JavaScript (ES6+) for logic
- Modular architecture with shared utilities

### Code Organization

**Common Utilities** (`web/js/common/`):

- `utils.js` - Helper functions (formatFileSize, showToast, etc.)
- `api.js` - Centralized EEL API calls
- `auth.js` - Session management
- `constants.js` - App-wide configuration

**Components** (`web/js/components/`):

- Reusable UI components (loader, sidebar, vault, etc.)

**Pages** (`web/js/pages/`):

- Page-specific logic separated from HTML

### Adding New Features

**Example EEL Function**:

```python
@eel.expose
def my_function(data):
    # Process data
    return {'success': True, 'data': result}
```

**Frontend Call**:

```javascript
const result = await eel.my_function(data)();
if (result.success) {
  // Handle success
}
```

### Contributing

1. Fork the repository
2. Create feature branch
3. Commit with clear messages
4. Submit pull request

### License

MIT License - See LICENSE file for details

---

## 📝 Version History

### v1.2.0 (Current)

- ✅ **New**: Modular JavaScript architecture
- ✅ **New**: Centralized API wrapper functions
- ✅ **New**: Common utility library
- ✅ **Improved**: Code organization and maintainability
- ✅ **Improved**: Performance optimizations
- ✅ **Removed**: Unused emotion detection code
- ✅ **Removed**: Redundant backend files

### v1.1.0

- ✅ Voice Stress Analysis Module
- ✅ Smart Device Detection
- ✅ Chunked Upload System
- ✅ Secure Vault System

### v1.0.0

- ✅ Real-time session recording
- ✅ File upload and processing
- ✅ Light/Dark theme support
- ✅ Professional reporting system

### Upcoming Features

- 🔜 Advanced analytics dashboard
- 🔜 Export functionality
- 🔜 Cloud storage integration
- 🔜 Mobile companion app

---

<div align="center">

**Developed with ❤️ by Ali Hamza-Coder**

_Empowering truth through technology_

</div>
