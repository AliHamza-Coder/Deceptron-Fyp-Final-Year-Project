# ========================================
# CAMERA FUNCTIONS MODULE
# Simple functions to control camera
# ========================================

import cv2

# ========================================
# CAMERA CONTROL FUNCTIONS
# ========================================

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
