# ========================================
# DECEPTRON - MAIN APPLICATION
# Deception Analysis System
# ========================================

import eel
import sys
import os
import re
import base64
import uuid
import time

from pathlib import Path

# ========================================
# PATH CONFIGURATION
# ========================================
# Resolve absolute paths relative to this script
BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
UPLOADS_DIR = WEB_DIR / "uploads"
RECORDINGS_DIR = WEB_DIR / "recordings"

# Ensure required directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

# Import our custom modules
# REMOVED: device_functions - JavaScript handles device enumeration directly
# REMOVED: camera_functions - No longer used
# REMOVED: emotion_functions - No longer using emotion detection
from modules import database

# ========================================
# INITIALIZE EEL
# ========================================

# Set web folder location
eel.init(str(WEB_DIR))

print("\n" + "="*60)
print("🚀 DECEPTRON - TRUTH VERIFICATION SYSTEM")
print("="*60 + "\n")

# ========================================
# LOAD EMOTION MODEL AT STARTUP
# ========================================
# REMOVED: Emotion detection disabled
# print("📦 Loading AI models...")
# emotion_model = emotion_functions.load_emotion_model()
# print("✅ All models loaded successfully!\n")

# ========================================
# EEL EXPOSED FUNCTIONS (callable from JavaScript)
# ========================================


# ========================================
# REMOVED: Emotion detection and device functions
# ========================================
# - process_frame() - Emotion detection disabled
# - get_available_cameras() - JavaScript handles device enumeration
# - get_available_microphones() - JavaScript handles device enumeration


# ========================================
# DATABASE & AUTHENTICATION FUNCTIONS
# ========================================

current_user = None

@eel.expose
def signup(user_data):
    """
    Handle user signup from the frontend.
    """
    try:
        print(f"📝 New signup attempt: {user_data.get('username')}")
        return database.signup_user(user_data)
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return {'success': False, 'message': str(e)}

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
        # Update last login timestamp
        database.update_last_login(current_user['username'])
        print(f"✅ Login successful: {current_user['username']}")
    return result

# Helper for consistent frontend responses
def response(success=True, data=None, message=""):
    return {
        "success": success,
        "data": data,
        "message": message
    }

@eel.expose
def logout():
    """Log out the current user (standardized)"""
    global current_user
    if current_user:
        print(f"🚪 User logged out: {current_user['username']}")
    current_user = None
    return response()

# ========================================
# REMOVED: Device enumeration functions
# ========================================
# JavaScript handles device enumeration directly via navigator.mediaDevices.enumerateDevices()
# - get_available_cameras() - REMOVED
# - get_available_microphones() - REMOVED

@eel.expose
def get_current_user():
    """Get current user (standardized)"""
    return response(data=current_user)

@eel.expose
def get_uploads():
    """Get user uploads (standardized)"""
    if not current_user:
        return response(success=False, message="Not logged in")
    data = database.get_user_uploads(current_user['username'])
    return response(data=data)

# Track active chunked uploads
active_uploads = {}

@eel.expose
def initiate_upload(filename, total_size, file_type, is_recording=False):
    """
    Prepare the server for a chunked upload.
    """
    try:
        if not current_user:
            return {'success': False, 'message': 'Not logged in'}
            
        upload_id = str(uuid.uuid4())
        safe_filename = re.sub(r'[^\w\-.]', '_', os.path.basename(filename))
        temp_path = UPLOADS_DIR / f"temp_{upload_id}"
        
        active_uploads[upload_id] = {
            'filename': safe_filename,
            'type': file_type,
            'size_str': total_size,
            'temp_path': temp_path,
            'username': current_user['username'],
            'is_recording': is_recording,
            'handle': open(temp_path, 'wb') # Open handle immediately for speed
        }
            
        return response(data={'upload_id': upload_id})
    except Exception as e:
        return response(success=False, message=str(e))

@eel.expose
def append_upload_chunk(upload_id, base64_data):
    """
    Append a chunk of data to an active upload using an open handle.
    """
    try:
        if upload_id not in active_uploads:
            return {'success': False, 'message': 'Upload session invalid'}
            
        upload_info = active_uploads[upload_id]
        
        # Faster decoding: only split if prefix is present
        if base64_data.startswith('data:'):
             base64_data = base64_data.split(',', 1)[1]
            
        file_content = base64.b64decode(base64_data)
        
        # Use existing handle
        upload_info['handle'].write(file_content)
            
        return {'success': True}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@eel.expose
def finalize_upload(upload_id):
    """
    Complete the upload by closing the handle, renaming, and adding a DB record.
    """
    try:
        if upload_id not in active_uploads:
            return {'success': False, 'message': 'Upload session invalid'}
            
        info = active_uploads.pop(upload_id)
        
        # Close handle before renaming
        if 'handle' in info:
            info['handle'].close()
            
        # Determine target directory based on type
        target_dir = UPLOADS_DIR
        relative_prefix = "../uploads/"
        
        # Check if this is a recording
        if info.get('is_recording'):
            target_dir = RECORDINGS_DIR
            relative_prefix = "../recordings/"
            
        # Ensure target directory exists
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)

        final_path = target_dir / info['filename']
        
        if final_path.exists():
            base, ext = os.path.splitext(info['filename'])
            final_path = target_dir / f"{base}_{int(time.time())}{ext}"
            info['filename'] = final_path.name

        os.rename(info['temp_path'], final_path)
        
        relative_path = f"{relative_prefix}{info['filename']}"
        return database.add_upload(info['username'], info['filename'], info['type'], info['size_str'], relative_path)
    except Exception as e:
        import traceback
        print(f"❌ Error finalizing upload: {e}")
        print(traceback.format_exc())
        return response(success=False, message=str(e))


@eel.expose
def save_recording(filename, base64_data, category):
    """
    Save a recorded session (video/audio) to the web/recordings directory.
    """
    try:
        if not current_user:
            return {'success': False, 'message': 'Not logged in'}
        
        # 1. Ensure recordings directory exists
        rec_dir = os.path.join('web', 'recordings')
        if not os.path.exists(rec_dir):
            os.makedirs(rec_dir)
            
        # 2. Clean filename and ensure extension
        safe_filename = re.sub(r'[^\w\-.]', '_', os.path.basename(filename))
        if not safe_filename.endswith('.webm'):
            safe_filename += '.webm'
            
        file_path = RECORDINGS_DIR / safe_filename
        
        # 3. Decode and save
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
            
        file_content = base64.b64decode(base64_data)
        with open(file_path, 'wb') as f:
            f.write(file_content)
            
        print(f"🎥 Recording saved: {file_path}")
        
        # 4. Add to database
        size_mb = f"{len(file_content) / (1024*1024):.1f} MB"
        relative_path = f"../recordings/{safe_filename}"
        
        return database.add_upload(
            current_user['username'], 
            safe_filename, 
            'video' if category == 'live' else 'audio', 
            size_mb, 
            relative_path
        )
        
    except Exception as e:
        print(f"❌ Error saving recording: {e}")
        return response(success=False, message=str(e))

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
                filename = os.path.basename(upload_data['filepath'])
                file_path = UPLOADS_DIR / filename
                
                if file_path.exists():
                    try:
                        file_path.unlink()
                        print(f"🗑️ Physically deleted: {file_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to delete physical file: {e}")
            
            return response()
        else:
            return result
            
    except Exception as e:
        print(f"❌ Error in delete_upload_record: {e}")
        return response(success=False, message=str(e))


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

@eel.expose
def save_preferences(preferences):
    """
    Save current user's preferences (e.g. camera/mic settings).
    """
    global current_user
    if not current_user:
        return {'success': False, 'message': 'Not logged in'}
    
    result = database.update_user_preferences(current_user['username'], preferences)
    if result['success']:
        # Update local session cache
        if 'preferences' not in current_user:
            current_user['preferences'] = {}
        current_user['preferences'].update(preferences)
    return result

@eel.expose
def load_preferences():
    """
    Load current user's preferences.
    """
    global current_user
    if not current_user:
        return {'success': False, 'message': 'Not logged in'}
    
    return database.get_user_preferences(current_user['username'])


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
