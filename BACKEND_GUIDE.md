# 🚀 DECEPTRON Backend Integration Guide

## 📦 Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If PyAudio installation fails on Windows, download the wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install manually.

---

## 🏃 Running the Application

```bash
python main.py
```

The application will:

1. Load the emotion detection AI model
2. Start the web server on port 8000
3. Open your browser automatically

---

## 🧩 Backend Modules Overview

### 1. `device_functions.py` - Device Detection

Simple functions to find cameras and microphones:

```python
# Find all cameras
cameras = find_all_cameras()
# Returns: [{'id': 0, 'name': 'Camera 0', 'working': True}, ...]

# Find all microphones
mics = find_all_microphones()
# Returns: [{'id': 0, 'name': 'Microphone (Realtek)', 'channels': 2}, ...]
```

### 2. `camera_functions.py` - Camera Control

Functions for camera operations:

```python
# Open camera
camera = initialize_camera(camera_id=0)

# Read frame
success, frame = read_frame(camera)

# Flip frame (mirror)
flipped = flip_frame(frame)

# Close camera
release_camera(camera)
```

### 3. `emotion_functions.py` - Emotion Detection

Functions for AI emotion recognition:

```python
# Load model (do this once at startup)
model = load_emotion_model()

# Detect face in frame
face_info = detect_face(frame)

# Get emotion from face crop
emotion, scores = get_emotion(face_crop)

# Format for frontend
data = format_emotion_data(emotion, scores)
```

---

## 🌐 Frontend Integration

### Include the JavaScript Helper

Add this to your HTML pages (already done in your existing pages):

```html
<script src="/eel.js"></script>
<script src="/js/backend_api.js"></script>
```

### Example: Real-time Emotion Detection

```javascript
// Get the video element
const videoElement = document.getElementById("webcam");

// Start detection
let detectionInterval = startEmotionDetection(
  videoElement,
  (result) => {
    if (result.face_found) {
      console.log(`Emotion: ${result.emotion}`);
      console.log(`Confidence: ${result.confidence}`);

      // Update your UI here
      document.getElementById("emotionLabel").innerText = result.emotion;
    }
  },
  500,
); // Check every 500ms (2 times per second)

// Stop detection when done
stopEmotionDetection(detectionInterval);
```

### Example: Get Available Devices

```javascript
// Get cameras
const cameras = await getAvailableCameras();
cameras.forEach((cam) => {
  console.log(`Camera ${cam.id}: ${cam.name}`);
});

// Get microphones
const mics = await getAvailableMicrophones();
mics.forEach((mic) => {
  console.log(`Mic ${mic.id}: ${mic.name}`);
});
```

---

## 📝 Python Backend API

### Exposed Functions (callable from JavaScript)

#### 1. `get_available_cameras()`

Returns list of all available cameras.

**JavaScript:**

```javascript
const cameras = await eel.get_available_cameras()();
```

**Returns:**

```json
[
  { "id": 0, "name": "Camera 0", "working": true },
  { "id": 1, "name": "Camera 1", "working": true }
]
```

#### 2. `get_available_microphones()`

Returns list of all available microphones.

**JavaScript:**

```javascript
const mics = await eel.get_available_microphones()();
```

**Returns:**

```json
[
  {
    "id": 0,
    "name": "Microphone (Realtek)",
    "channels": 2,
    "sample_rate": 44100
  }
]
```

#### 3. `process_frame(base64_image)`

Detects emotion from a camera frame.

**JavaScript:**

```javascript
const result = await eel.process_frame(base64Image)();
```

**Returns:**

```json
{
  "success": true,
  "face_found": true,
  "emotion": "Happy",
  "confidence": 0.85,
  "all_scores": {
    "Anger": 0.02,
    "Happiness": 0.85,
    "Neutral": 0.1,
    "Sadness": 0.03
  },
  "face_box": { "x": 100, "y": 50, "w": 200, "h": 250 }
}
```

---

## 🎯 Quick Integration Examples

### For `live-session.html` and `facial-expression.html`

Add this JavaScript after the camera is turned on:

```javascript
// After camera is activated
let emotionDetectionInterval = null;

async function toggleCamera() {
  // ... your existing camera code ...

  if (cameraOn) {
    // Start emotion detection
    const videoElement = document.getElementById("webcam");
    emotionDetectionInterval = startEmotionDetection(videoElement, (result) => {
      if (result.face_found) {
        // Update UI with emotion
        console.log(`Detected: ${result.emotion} (${result.confidence})`);
        // Add your UI update code here
      }
    });
  } else {
    // Stop emotion detection
    stopEmotionDetection(emotionDetectionInterval);
  }
}
```

---

## 🔧 Troubleshooting

### PyAudio Installation Error

Download the appropriate `.whl` file for your Python version from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install:

```bash
pip install PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl
```

### Camera Not Detected

- Make sure no other application is using the camera
- Try different camera IDs (0, 1, 2, etc.)
- Check camera permissions in Windows Settings

### Model Loading Error

- Ensure you have a stable internet connection (first run downloads the model)
- Check that you have enough disk space (~500MB for models)

---

## 📚 Code Structure

```
Frontend/
├── main.py                    # Main application with Eel server
├── requirements.txt           # Python dependencies
├── modules/
│   ├── device_functions.py    # Camera/mic detection
│   ├── camera_functions.py    # Camera control
│   └── emotion_functions.py   # AI emotion detection
└── web/
    ├── js/
    │   └── backend_api.js     # JavaScript helper functions
    └── pages/
        ├── welcome.html
        ├── live-session.html
        └── facial-expression.html
```

---

## ✅ Summary

- **No UI changes** - Your existing design stays the same
- **Simple functions** - No classes, just parameter passing
- **Beginner-friendly** - Clear comments in every file
- **Real-time** - Fast communication between frontend and backend
- **Modular** - Each function does ONE thing

**You're all set!** 🎉
