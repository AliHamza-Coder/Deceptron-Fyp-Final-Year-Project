# ========================================
# DECEPTRON - MAIN APPLICATION
# Real-time Emotion Detection System
# ========================================

import eel
import sys

# Import our custom modules
from modules import device_functions
from modules import camera_functions
from modules import emotion_functions

# ========================================
# INITIALIZE EEL
# ========================================

# Set web folder location
eel.init('web')

print("\n" + "="*60)
print("🚀 DECEPTRON - TRUTH VERIFICATION SYSTEM")
print("="*60 + "\n")

# ========================================
# LOAD EMOTION MODEL AT STARTUP
# ========================================

print("📦 Loading AI models...")
emotion_model = emotion_functions.load_emotion_model()
print("✅ All models loaded successfully!\n")

# ========================================
# EEL EXPOSED FUNCTIONS (callable from JavaScript)
# ========================================

@eel.expose
def get_available_cameras():
    """
    Get list of all available cameras.
    Called from JavaScript to populate camera dropdown.
    
    Returns:
        list: List of camera dictionaries
    """
    print("🔍 Frontend requested camera list")
    cameras = device_functions.find_all_cameras()
    return cameras


@eel.expose
def get_available_microphones():
    """
    Get list of all available microphones.
    Called from JavaScript to populate microphone dropdown.
    
    Returns:
        list: List of microphone dictionaries
    """
    print("🔍 Frontend requested microphone list")
    mics = device_functions.find_all_microphones()
    return mics


@eel.expose
def process_frame(base64_image):
    """
    Process a single frame from the frontend camera.
    This is the MAIN function for real-time emotion detection.
    
    Parameters:
        base64_image (str): Base64 encoded image from JavaScript
    
    Returns:
        dict: Emotion detection results
              Example: {
                  'success': True,
                  'face_found': True,
                  'emotion': 'Happy',
                  'confidence': 0.85,
                  'all_scores': {...}
              }
    """
    try:
        # Step 1: Decode base64 image to OpenCV frame
        frame = camera_functions.decode_base64_to_frame(base64_image)
        
        # Check if frame is None (not using == to avoid array comparison)
        if frame is None:
            return {
                'success': False,
                'error': 'Failed to decode image'
            }
        
        # Step 2: Detect face in frame
        face_info = emotion_functions.detect_face(frame)
        
        if not face_info['found']:
            return {
                'success': True,
                'face_found': False,
                'emotion': 'No Face',
                'confidence': 0.0
            }
        
        # Step 3: Extract face crop
        x = face_info['x']
        y = face_info['y']
        w = face_info['w']
        h = face_info['h']
        
        # Make sure we have valid coordinates
        if w <= 0 or h <= 0:
            return {
                'success': True,
                'face_found': False,
                'emotion': 'Invalid Face',
                'confidence': 0.0
            }
        
        face_crop = frame[y:y+h, x:x+w]
        
        # Step 4: Get emotion from face
        emotion, scores = emotion_functions.get_emotion(face_crop)
        
        # Check if emotion detection failed
        if emotion is None:
            return {
                'success': True,
                'face_found': True,
                'emotion': 'Unknown',
                'confidence': 0.0
            }
        
        # Step 5: Format results
        emotion_data = emotion_functions.format_emotion_data(emotion, scores)
        
        # Step 6: Return results to frontend
        return {
            'success': True,
            'face_found': True,
            'emotion': emotion_data['emotion'],
            'confidence': emotion_data['confidence'],
            'all_scores': emotion_data['all_scores'],
            'face_box': face_info  # Include face coordinates for drawing
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Error processing frame: {e}")
        print(traceback.format_exc())
        return {
            'success': False,
            'error': str(e)
        }


# ========================================
# START THE APPLICATION
# ========================================

if __name__ == "__main__":
    print("="*60)
    print("🌐 Starting DECEPTRON Desktop App...")
    print("="*60 + "\n")
    
    try:
        # Start Eel - will open in default browser or Edge
        eel.start(
            'pages/welcome.html',  # Starting page
            size=(1400, 900),      # Window size
            port=8000,             # Port number
            mode=None,             # Let Eel choose best available browser
            close_callback=lambda page, sockets: None  # Prevent exit on close
        )
    except (SystemExit, KeyboardInterrupt):
        print("\n\n" + "="*60)
        print("👋 Shutting down DECEPTRON...")
        print("="*60)
        sys.exit()
    except EnvironmentError:
        # Fallback if no browser found
        print("⚠️  No suitable browser found. Opening in default browser...")
        eel.start('pages/welcome.html', size=(1400, 900), port=8000)
