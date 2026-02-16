# ========================================
# DEVICE DETECTION MODULE
# Simple functions to find cameras and microphones
# ========================================

import cv2
import pyaudio

# ========================================
# CAMERA DETECTION FUNCTIONS
# ========================================

def find_all_cameras():
    """
    Find all available cameras on the system.
    
    Returns:
        list: List of dictionaries with camera info
              Example: [{'id': 0, 'name': 'Integrated Camera', 'working': True}, ...]
    """
    print("🔍 Scanning for cameras...")
    available_cameras = []
    
    # Try camera indices 0 to 10
    for camera_id in range(10):
        # Try to open camera with DirectShow (Windows)
        camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        
        if camera.isOpened():
            # Camera is available
            camera_info = {
                'id': camera_id,
                'name': f'Camera {camera_id}',
                'working': True
            }
            available_cameras.append(camera_info)
            print(f"  ✅ Found: Camera {camera_id}")
            camera.release()
        else:
            # No camera at this index
            pass
    
    print(f"📷 Total cameras found: {len(available_cameras)}")
    return available_cameras




# ========================================
# MICROPHONE DETECTION FUNCTIONS
# ========================================

def find_all_microphones():
    """
    Find all available microphones on the system.
    
    Returns:
        list: List of dictionaries with microphone info
              Example: [{'id': 0, 'name': 'Microphone (Realtek)', 'channels': 2}, ...]
    """
    print("🔍 Scanning for microphones...")
    available_mics = []
    
    try:
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Get number of audio devices
        device_count = audio.get_device_count()
        
        # Loop through all devices
        for device_id in range(device_count):
            device_info = audio.get_device_info_by_index(device_id)
            
            # Check if device has input channels (is a microphone)
            if device_info['maxInputChannels'] > 0:
                mic_info = {
                    'id': device_id,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': int(device_info['defaultSampleRate'])
                }
                available_mics.append(mic_info)
                print(f"  ✅ Found: {device_info['name']}")
        
        # Close PyAudio
        audio.terminate()
        
    except Exception as e:
        print(f"❌ Error scanning microphones: {e}")
        return []
    
    print(f"🎤 Total microphones found: {len(available_mics)}")
    return available_mics


# ========================================
# TEST CODE (runs when you execute this file directly)
# ========================================

# No test code - purely for import
pass
