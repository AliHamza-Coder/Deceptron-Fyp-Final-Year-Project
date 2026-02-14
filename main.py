# ========================================
# DECEPTRON - MAIN APPLICATION
# Real-time Emotion Detection System
# ========================================

import eel
import sys
import os
import base64
import uuid
import time

# Import our custom modules
from modules import device_functions
from modules import camera_functions
from modules import emotion_functions
from modules import database

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
# DATABASE & AUTHENTICATION FUNCTIONS
# ========================================

current_user = None

@eel.expose
def signup(user_data):
    """
    Handle user signup from the frontend.
    """
    print(f"📝 New signup attempt: {user_data.get('username')}")
    return database.signup_user(user_data)

@eel.expose
def login(identity, password):
    """
    Handle user login from the frontend.
    """
    global current_user
    print(f"🔑 Login attempt for: {identity}")
    result = database.login_user(identity, password)
    if result['success']:
        current_user = result['user']
        print(f"✅ Login successful: {current_user['username']}")
    return result

@eel.expose
def logout():
    """
    Log out the current user.
    """
    global current_user
    if current_user:
        print(f"🚪 User logged out: {current_user['username']}")
    current_user = None
    return {'success': True}

@eel.expose
def get_current_user():
    """
    Get the currently logged-in user information.
    """
    return current_user

@eel.expose
def get_uploads():
    """
    Get all uploads for the currently logged-in user.
    """
    if not current_user:
        return []
    return database.get_user_uploads(current_user['username'])

# Track active chunked uploads
active_uploads = {}

@eel.expose
def initiate_upload(filename, total_size, file_type):
    """
    Prepare the server for a chunked upload.
    """
    try:
        if not current_user:
            return {'success': False, 'message': 'Not logged in'}
            
        upload_id = str(uuid.uuid4())
        safe_filename = filename.replace(' ', '_')
        
        upload_dir = os.path.join('web', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        temp_path = os.path.join(upload_dir, f"temp_{upload_id}")
        
        active_uploads[upload_id] = {
            'filename': safe_filename,
            'type': file_type,
            'size_str': total_size, # This is the formatted string from frontend
            'temp_path': temp_path,
            'username': current_user['username']
        }
        
        # Create/Clear temp file
        with open(temp_path, 'wb') as f:
            pass
            
        return {'success': True, 'upload_id': upload_id}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@eel.expose
def append_upload_chunk(upload_id, base64_data):
    """
    Append a chunk of data to an active upload.
    """
    try:
        if upload_id not in active_uploads:
            return {'success': False, 'message': 'Upload session invalid'}
            
        upload_info = active_uploads[upload_id]
        
        # Decode base64 data
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
            
        file_content = base64.b64decode(base64_data)
        
        with open(upload_info['temp_path'], 'ab') as f:
            f.write(file_content)
            
        return {'success': True}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@eel.expose
def finalize_upload(upload_id):
    """
    Complete the upload by renaming the temp file and adding a DB record.
    """
    try:
        if upload_id not in active_uploads:
            return {'success': False, 'message': 'Upload session invalid'}
            
        info = active_uploads.pop(upload_id)
        final_path = os.path.join('web', 'uploads', info['filename'])
        
        # Handle filename collisions if necessary (optional)
        if os.path.exists(final_path):
            base, ext = os.path.splitext(info['filename'])
            final_path = os.path.join('web', 'uploads', f"{base}_{int(time.time())}{ext}")
            info['filename'] = os.path.basename(final_path)

        os.rename(info['temp_path'], final_path)
        
        relative_path = f"../uploads/{info['filename']}"
        return database.add_upload(info['username'], info['filename'], info['type'], info['size_str'], relative_path)
    except Exception as e:
        return {'success': False, 'message': str(e)}

@eel.expose
def add_upload_record(filename, file_type, file_size, base64_data):
    """
    Physically save the file and add a record to the database.
    """
    try:
        if not current_user:
            return {'success': False, 'message': 'Not logged in'}
        
        # 1. Clean filename
        safe_filename = filename.replace(' ', '_')
        
        # 2. Save file physically to web/uploads/
        upload_dir = os.path.join('web', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        file_path = os.path.join(upload_dir, safe_filename)
        
        # Decode base64 data
        try:
            # Extract header if present (e.g., "data:audio/wav;base64,")
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
                
            file_content = base64.b64decode(base64_data)
            with open(file_path, 'wb') as f:
                f.write(file_content)
                
            print(f"📦 Physically saved: {file_path}")
        except Exception as e:
            print(f"❌ Error saving file physically: {e}")
            return {'success': False, 'message': f'File saving failed: {str(e)}'}

        # 3. Add to database with the relative path for the frontend
        relative_path = f"../uploads/{safe_filename}"
        return database.add_upload(current_user['username'], safe_filename, file_type, file_size, relative_path)
        
    except Exception as e:
        print(f"❌ General error in add_upload_record: {e}")
        return {'success': False, 'message': str(e)}

@eel.expose
def delete_upload_record(upload_id):
    """
    Delete an upload record and its physical file.
    """
    try:
        if not current_user:
            return {'success': False, 'message': 'Not logged in'}
        
        # 1. Delete from database
        result = database.delete_upload(upload_id, current_user['username'])
        
        if result['success']:
            # 2. Try to delete the physical file
            upload_data = result.get('data')
            if upload_data and 'filepath' in upload_data:
                # Relative path is typically "../uploads/filename"
                # We need the actual system path: web/uploads/filename
                filename = os.path.basename(upload_data['filepath'])
                file_path = os.path.join('web', 'uploads', filename)
                
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"🗑️ Physically deleted: {file_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to delete physical file: {e}")
            
            return {'success': True}
        else:
            return result
            
    except Exception as e:
        print(f"❌ Error in delete_upload_record: {e}")
        return {'success': False, 'message': str(e)}


@eel.expose
def update_profile(name, title):
    """
    Update current user's profile information.
    """
    global current_user
    if not current_user:
        return {'success': False, 'message': 'Not logged in'}
    
    result = database.update_user_profile(current_user['username'], {'fullname': name, 'title': title})
    if result['success']:
        current_user = result['user']
    return result

@eel.expose
def update_avatar(avatar_base64):
    """
    Update current user's profile avatar.
    """
    global current_user
    if not current_user:
        return {'success': False, 'message': 'Not logged in'}
    
    result = database.update_user_profile(current_user['username'], {'avatar': avatar_base64})
    if result['success']:
        current_user = result['user']
    return result

@eel.expose
def update_password(current_pwd, new_pwd):
    """
    Update current user's password.
    """
    if not current_user:
        return {'success': False, 'message': 'Not logged in'}
    return database.change_password(current_user['username'], current_pwd, new_pwd)


# ========================================
# START THE APPLICATION
# ========================================

if __name__ == "__main__":
    print("="*60)
    print("🌐 Starting DECEPTRON Desktop App...")
    print("="*60 + "\n")
    
    try:
        # Force 'chrome' for a true desktop app feel. If Chrome isn't found, Eel will try others.
        # Setting port to 0 lets Eel find any available open port.
        print("🖥️  Opening desktop window...")
        eel.start(
            'index.html',
            size=(1500, 950),
            port=0, 
            mode='chrome',
            close_callback=lambda page, sockets: None
        )
    except (SystemExit, KeyboardInterrupt):
        print("\n\n" + "="*60)
        print("👋 Shutting down DECEPTRON...")
        print("="*60)
        sys.exit()
    except EnvironmentError:
        # Fallback if no browser found
        print("⚠️  No suitable browser found. Opening in default browser...")
        eel.start('index.html', size=(1400, 900), port=8000)
