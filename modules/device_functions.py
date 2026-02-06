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


def test_camera(camera_id):
    """
    Test if a specific camera ID works.
    
    Parameters:
        camera_id (int): The camera index to test
    
    Returns:
        bool: True if camera works, False otherwise
    """
    camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    is_working = camera.isOpened()
    camera.release()
    return is_working


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


def get_device_info(device_id, device_type='camera'):
    """
    Get detailed information about a specific device.
    
    Parameters:
        device_id (int): The device index
        device_type (str): Either 'camera' or 'microphone'
    
    Returns:
        dict: Device information or None if not found
    """
    if device_type == 'camera':
        if test_camera(device_id):
            return {'id': device_id, 'name': f'Camera {device_id}', 'type': 'camera'}
        else:
            return None
    
    elif device_type == 'microphone':
        try:
            audio = pyaudio.PyAudio()
            device_info = audio.get_device_info_by_index(device_id)
            audio.terminate()
            
            if device_info['maxInputChannels'] > 0:
                return {
                    'id': device_id,
                    'name': device_info['name'],
                    'type': 'microphone',
                    'channels': device_info['maxInputChannels']
                }
        except:
            return None
    
    return None


# ========================================
# TEST CODE (runs when you execute this file directly)
# ========================================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("DEVICE DETECTION TEST")
    print("="*50 + "\n")
    
    # Test camera detection
    cameras = find_all_cameras()
    print(f"\nCameras: {cameras}\n")
    
    # Test microphone detection
    mics = find_all_microphones()
    print(f"\nMicrophones: {mics}\n")
    
    print("="*50)
    print("TEST COMPLETE")
    print("="*50)
