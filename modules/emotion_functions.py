# ========================================
# EMOTION DETECTION MODULE
# Simple functions for detecting emotions from faces
# ========================================

import cv2
import torch
import mediapipe as mp
from hsemotion.facial_emotions import HSEmotionRecognizer

# ========================================
# GLOBAL VARIABLES (loaded once at startup)
# ========================================

# MediaPipe face detection
mp_face_detection = mp.solutions.face_detection
face_detector = None

# Emotion recognition model
emotion_model = None

# ========================================
# MODEL LOADING FUNCTIONS
# ========================================

def load_emotion_model(model_name='enet_b0_8_best_vgaf'):
    """
    Load the emotion detection model.
    This should be called ONCE at application startup.
    
    Parameters:
        model_name (str): Model to use for emotion detection
                         Options: 'enet_b0_8_best_vgaf', 'enet_b0_8_best_afew', 
                                 'enet_b2_8', 'enet_b0_8_va_mtl', 'enet_b2_7'
    
    Returns:
        model: Loaded emotion recognition model
    """
    global emotion_model, face_detector
    
    print(f"🧠 Loading emotion detection model: {model_name}...")
    
    # Detect device (GPU or CPU)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"   Using device: {device}")
    
    try:
        # Try to load model
        emotion_model = HSEmotionRecognizer(model_name=model_name, device=device)
        print("✅ Emotion model loaded successfully")
    except Exception as e:
        # Handle torch.load compatibility issue
        if "WeightsUnpickler" in str(e) or "unpickle" in str(e):
            print("⚠️  Patching torch.load for compatibility...")
            original_load = torch.load
            torch.load = lambda *args, **kwargs: original_load(*args, **{**kwargs, 'weights_only': False})
            emotion_model = HSEmotionRecognizer(model_name=model_name, device=device)
            torch.load = original_load
            print("✅ Emotion model loaded successfully (with patch)")
        else:
            raise e
    
    # Initialize MediaPipe face detection
    print("👤 Loading face detection model...")
    face_detector = mp_face_detection.FaceDetection(
        model_selection=1,  # 1 = full range model (better for farther faces)
        min_detection_confidence=0.5
    )
    print("✅ Face detection model loaded successfully")
    
    return emotion_model


def detect_face(frame):
    """
    Detect face in the frame using MediaPipe.
    
    Parameters:
        frame (numpy array): Image frame in BGR format (OpenCV default)
    
    Returns:
        dict: Face information with bounding box coordinates
              Example: {'x': 100, 'y': 50, 'w': 200, 'h': 250, 'found': True}
              Returns {'found': False} if no face detected
    """
    global face_detector
    
    if frame is None or face_detector is None:
        return {'found': False}
    
    # Convert BGR to RGB (MediaPipe uses RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces
    results = face_detector.process(rgb_frame)
    
    if results.detections:
        # Get first detected face
        detection = results.detections[0]
        
        # Get bounding box
        bboxC = detection.location_data.relative_bounding_box
        height, width, _ = frame.shape
        
        # Convert relative coordinates to absolute pixels
        x = int(bboxC.xmin * width)
        y = int(bboxC.ymin * height)
        w = int(bboxC.width * width)
        h = int(bboxC.height * height)
        
        # Make sure coordinates are within frame bounds
        x = max(0, x)
        y = max(0, y)
        w = min(width - x, w)
        h = min(height - y, h)
        
        return {
            'x': x,
            'y': y,
            'w': w,
            'h': h,
            'found': True
        }
    else:
        return {'found': False}


def get_emotion(face_crop, model=None):
    """
    Detect emotion from a cropped face image.
    
    Parameters:
        face_crop (numpy array): Cropped face image in BGR format
        model: Emotion recognition model (uses global if None)
    
    Returns:
        tuple: (emotion_label, confidence_scores)
               emotion_label (str): Detected emotion (e.g., "Happy", "Sad")
               confidence_scores (dict): Confidence for each emotion
    """
    global emotion_model
    
    # Use global model if not provided
    if model is None:
        model = emotion_model
    
    # Check if face_crop is valid
    if face_crop is None or model is None:
        return None, {}
    
    # Check if face_crop is empty (size == 0)
    if face_crop.size == 0:
        return None, {}
    
    try:
        # Predict emotion (HSEmotion expects BGR image)
        emotion, scores = model.predict_emotions(face_crop, logits=False)
        return emotion, scores
    except Exception as e:
        print(f"❌ Error detecting emotion: {e}")
        return None, {}


def format_emotion_data(emotion, scores):
    """
    Format emotion data into a clean dictionary for sending to frontend.
    
    Parameters:
        emotion (str): Detected emotion label
        scores (numpy array): Confidence scores array from HSEmotion
    
    Returns:
        dict: Formatted emotion data
              Example: {'emotion': 'Happy', 'confidence': 0.85, 'all_scores': {...}}
    """
    if emotion is None:
        return {
            'emotion': 'Unknown',
            'confidence': 0.0,
            'all_scores': {}
        }
    
    # HSEmotion returns scores as a numpy array
    # Emotion labels in order: Anger, Contempt, Disgust, Fear, Happiness, Neutral, Sadness, Surprise
    emotion_labels = ['Anger', 'Contempt', 'Disgust', 'Fear', 'Happiness', 'Neutral', 'Sadness', 'Surprise']
    
    # Convert numpy array to dictionary
    import numpy as np
    if isinstance(scores, np.ndarray):
        scores_dict = {label: float(score) for label, score in zip(emotion_labels, scores)}
    elif isinstance(scores, (list, tuple)):
        scores_dict = {label: float(score) for label, score in zip(emotion_labels, scores)}
    elif isinstance(scores, dict):
        scores_dict = scores
    else:
        scores_dict = {}
    
    # Get confidence for detected emotion
    # Use .get() to safely retrieve value
    confidence = scores_dict.get(emotion, 0.0)
    
    return {
        'emotion': emotion,
        'confidence': float(confidence),
        'all_scores': scores_dict
    }


# ========================================
# TEST CODE (runs when you execute this file directly)
# ========================================

# ========================================
# TEST CODE (runs when you execute this file directly)
# ========================================

# No test code - purely for import
pass
