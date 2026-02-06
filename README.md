# DECEPTRON - Advanced Truth Verification System

DECEPTRON is a cutting-edge hybrid desktop application designed for advanced truth verification using multi-modal analysis. It combines a high-performance Python backend for AI/ML processing with a modern, responsive JavaScript-based frontend for a seamless user experience.

## 🚀 Features

- **Real-time Analysis Dashboard**: Centralized hub for all verification activities.
- **Live Session Mode**: Conduct interviews with real-time feedback.
- **Facial Expression Analysis**: Detect micro-expressions and emotional cues using computer vision.
- **Voice Stress Analysis**: Analyze vocal patterns for signs of deception.
- **Detailed Reporting**: Generation of comprehensive reports with data visualization (`report-detail.html`).
- **Uploads & File Processing**: Analyze pre-recorded media.
- **Secure Authentication**: Integrated Login and Signup workflow.
- **Customizable Settings**: Light/Dark modes, parameter tuning.

## 🛠 Tech Stack

- **Backend**: Python (Logic, AI Models, File I/O)
- **Frontend**: HTML5, CSS3, JavaScript (UI, Camera Handling, Charts)
- **Middleware**: **Eel** (Bridges Python and JavaScript)

## 📦 Installation & Setup

1.  **Prerequisites**:
    - Python 3.8 or higher installed.
    - Modern Web Browser (Chrome/Edge) installed.

2.  **Clone/Download the Repository**.

3.  **Set up the Virtual Environment** (Recommended):
    - Windows:
      ```bash
      python -m venv myenv
      myenv\Scripts\activate
      ```

4.  **Install Dependencies**:
    ```bash
    pip install eel
    # Add other future AI dependencies here (e.g., opencv-python, numpy)
    ```

## 🖥️ How to Run

**Option 1: Quick Launch (Windows)**
Double-click the `RUN.bat` file in the root directory.

**Option 2: Manual Start**
Open your terminal in the project folder and run:

```bash
# Ensure your environment is active
python main.py
```

The application will launch in a dedicated application window.

## 🏗️ Architecture & Development Guide

### How it Works

DECEPTRON uses **Eel** to host a local web server that communicates with a Python backend.

1.  **Frontend (`/web`)**: Handles the User Interface, animations, and camera inputs. To open a camera:
    - Use Standard HTML5/JS: `navigator.mediaDevices.getUserMedia()` for the smoothest video preview.
2.  **Backend (`main.py`)**: Handles the heavy lifting.
    - Use Python for: Database storage, complex math, running AI models (PyTorch/TensorFlow), and saving reports.

### Adding New Features (Best Practices)

- **Camera/Video**:
  - **Display**: strict usage of JavaScript (Frontend) for showing the live feed to the user.
  - **Processing**: Capture frames in JS, send them to Python via `eel.process_frame(data_url)`, analyze in Python with OpenCV, and return the result.
- **Charts**: Use JavaScript libraries (like Chart.js) in the frontend. Fetch the _data_ from Python.

## 📂 Project Structure

```
DEceptron Screens/Frontend/
├── main.py              # Entry point & Python backend logic
├── RUN.bat              # One-click launcher
├── web/                 # Frontend Assets
│   ├── pages/           # HTML Views (Dashboard, Live Session, etc.)
│   ├── scripts/         # JavaScript logic
│   ├── styles/          # CSS Stylesheets
│   └── assets/          # Images and Icons
└── myenv/               # Python Virtual Environment
```

---

**Developed by Ali Hamza-Coder**
