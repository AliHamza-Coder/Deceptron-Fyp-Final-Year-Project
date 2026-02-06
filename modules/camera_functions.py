# ========================================
# CAMERA FUNCTIONS MODULE
# Simple functions to control camera
# ========================================

import cv2

# ========================================
# CAMERA CONTROL FUNCTIONS
# ========================================

def initialize_camera(camera_id=0):
    """
    Open and initialize a camera.
    
    Parameters:
        camera_id (int): Camera index (0 = default camera, 1 = external camera, etc.)
    
    Returns:
        camera object: OpenCV VideoCapture object, or None if failed
    """
    print(f"📷 Opening camera {camera_id}...")
    
    # Open camera with DirectShow backend (Windows)
    camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    
    if camera.isOpened():
        print(f"✅ Camera {camera_id} opened successfully")
        return camera
    else:
        print(f"❌ Failed to open camera {camera_id}")
        return None


def read_frame(camera):
    """
    Read one frame from the camera.
    
    Parameters:
        camera: OpenCV VideoCapture object
    
    Returns:
        tuple: (success, frame)
               success (bool): True if frame was read successfully
               frame (numpy array): The image frame, or None if failed
    """
    if camera is None:
        return False, None
    
    # Read frame from camera
    success, frame = camera.read()
    
    return success, frame


def flip_frame(frame):
    """
    Flip the frame horizontally (mirror effect).
    
    Parameters:
        frame (numpy array): The image frame to flip
    
    Returns:
        numpy array: Flipped frame
    """
    if frame is None:
        return None
    
    # Flip horizontally (1 means horizontal flip)
    flipped_frame = cv2.flip(frame, 1)
    
    return flipped_frame


def release_camera(camera):
    """
    Close and release the camera.
    
    Parameters:
        camera: OpenCV VideoCapture object
    
    Returns:
        None
    """
    if camera is not None:
        camera.release()
        print("📷 Camera released")


def encode_frame_to_base64(frame):
    """
    Convert frame to base64 string for sending to frontend.
    
    Parameters:
        frame (numpy array): The image frame
    
    Returns:
        str: Base64 encoded JPEG image
    """
    import base64
    
    if frame is None:
        return None
    
    # Encode frame as JPEG
    success, buffer = cv2.imencode('.jpg', frame)
    
    if success:
        # Convert to base64 string
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        return jpg_as_text
    else:
        return None


def decode_base64_to_frame(base64_string):
    """
    Convert base64 string from frontend to OpenCV frame.
    
    Parameters:
        base64_string (str): Base64 encoded image
    
    Returns:
        numpy array: OpenCV frame (BGR format)
    """
    import base64
    import numpy as np
    
    if base64_string is None:
        return None
    
    try:
        # Remove data URL prefix if present
        if 'base64,' in base64_string:
            base64_string = base64_string.split('base64,')[1]
        
        # Decode base64 to bytes
        img_bytes = base64.b64decode(base64_string)
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(img_bytes, np.uint8)
        
        # Decode image
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return frame
    except Exception as e:
        print(f"❌ Error decoding base64: {e}")
        return None


# ========================================
# TEST CODE (runs when you execute this file directly)
# ========================================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("CAMERA FUNCTIONS TEST")
    print("="*50 + "\n")
    
    # Test camera initialization
    cam = initialize_camera(0)
    
    if cam is not None:
        # Read a frame
        success, frame = read_frame(cam)
        
        if success:
            print(f"✅ Frame captured: {frame.shape}")
            
            # Flip frame
            flipped = flip_frame(frame)
            print(f"✅ Frame flipped: {flipped.shape}")
            
            # Test base64 encoding
            base64_img = encode_frame_to_base64(frame)
            if base64_img:
                print(f"✅ Frame encoded to base64 (length: {len(base64_img)})")
                
                # Test decoding
                decoded_frame = decode_base64_to_frame(base64_img)
                if decoded_frame is not None:
                    print(f"✅ Frame decoded from base64: {decoded_frame.shape}")
        
        # Release camera
        release_camera(cam)
    
    print("\n" + "="*50)
    print("TEST COMPLETE")
    print("="*50)
