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

import config as app_config
BACKEND_URL = app_config.BACKEND_URL

# Persistent storage directory (survives app restarts and PyInstaller extraction)
DATA_DIR = Path.home() / ".deceptron"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Import our custom modules
from modules import database

# ========================================
# INITIALIZE EEL
# ========================================

# Set web folder location
eel.init(str(WEB_DIR))

# Custom route to serve local persistent data (uploads/recordings) to the UI
# This is necessary because these files are outside the Eel WEB_DIR
@eel.btl.route('/data/<filepath:path>')
def server_static(filepath):
    return eel.btl.static_file(filepath, root=str(DATA_DIR))

print("\n" + "="*60)
print("🚀 DECEPTRON - TRUTH VERIFICATION SYSTEM")
print("="*60 + "\n")

# ========================================
# LOAD EMOTION MODEL AT STARTUP
# ========================================
# Emotion detection is currently disabled and no model is loaded at startup.

# ========================================
# EEL EXPOSED FUNCTIONS (callable from JavaScript)
# ========================================


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

def _get_user_dirs(username):
    user_dir = DATA_DIR / username
    return {
        'uploads': user_dir / "uploads",
        'recordings': user_dir / "recordings",
    }

@eel.expose
def logout():
    """Log out the current user (standardized)"""
    global current_user
    if current_user:
        print(f"🚪 User logged out: {current_user['username']}")
    current_user = None
    return response()

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
        
        dirs = _get_user_dirs(current_user['username'])
        target_dir = dirs['recordings'] if is_recording else dirs['uploads']
        target_dir.mkdir(parents=True, exist_ok=True)
        temp_path = target_dir / f"temp_{upload_id}"
        
        active_uploads[upload_id] = {
            'filename': safe_filename,
            'type': file_type,
            'size_str': total_size,
            'temp_path': temp_path,
            'username': current_user['username'],
            'is_recording': is_recording,
            'handle': open(temp_path, 'wb')
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
        
        if 'handle' in info:
            info['handle'].close()
            
        username = info['username']
        dirs = _get_user_dirs(username)
        target_dir = dirs['recordings'] if info.get('is_recording') else dirs['uploads']
        route_prefix = f"/data/{username}/recordings/" if info.get('is_recording') else f"/data/{username}/uploads/"
        
        target_dir.mkdir(parents=True, exist_ok=True)

        final_path = target_dir / info['filename']
        
        if final_path.exists():
            base, ext = os.path.splitext(info['filename'])
            final_path = target_dir / f"{base}_{int(time.time())}{ext}"
            info['filename'] = final_path.name

        os.rename(info['temp_path'], final_path)
        
        relative_path = f"{route_prefix}{info['filename']}"
        return database.add_upload(username, info['filename'], info['type'], info['size_str'], relative_path)
    except Exception as e:
        import traceback
        print(f"❌ Error finalizing upload: {e}")
        print(traceback.format_exc())
        return response(success=False, message=str(e))


@eel.expose
def save_recording(filename, base64_data, category):
    """
    Save a recorded session (video/audio) to the persistent recordings directory.
    """
    try:
        if not current_user:
            return {'success': False, 'message': 'Not logged in'}
        
        username = current_user['username']
        dirs = _get_user_dirs(username)
        rec_dir = dirs['recordings']
        rec_dir.mkdir(parents=True, exist_ok=True)
        
        safe_filename = re.sub(r'[^\w\-.]', '_', os.path.basename(filename))
        base, _ = os.path.splitext(safe_filename)
        safe_filename = base + '.mp4'
            
        file_path = rec_dir / safe_filename
        
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
            
        file_content = base64.b64decode(base64_data)
        with open(file_path, 'wb') as f:
            f.write(file_content)
            
        print(f"🎥 Recording saved: {file_path}")
        
        size_mb = f"{len(file_content) / (1024*1024):.1f} MB"
        relative_path = f"/data/{username}/recordings/{safe_filename}"
        
        return database.add_upload(
            username, 
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
        
        result = database.delete_upload(upload_id, current_user['username'])
        
        if result['success']:
            upload_data = result.get('data')
            if upload_data and 'filepath' in upload_data:
                db_path = upload_data['filepath']
                if db_path.startswith('/data/'):
                    relative_to_data = db_path.replace('/data/', '', 1)
                    file_path = DATA_DIR / relative_to_data
                    
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


@eel.expose
def run_voice_analysis(relative_path):
    """Bridge to FastAPI Voice Analysis"""
    try:
        import requests
        clean_path = relative_path.replace('/data/', '', 1)
        abs_path = str(DATA_DIR / clean_path)
        
        print(f"🎤 Running Voice Analysis on: {abs_path}")
        response = requests.get(f"{BACKEND_URL}/analyze/voice?file_path={abs_path}")
        return response.json()
    except Exception as e:
        print(f"❌ Voice API Error: {e}")
        return {'success': False, 'message': str(e)}

@eel.expose
def run_emotion_analysis(relative_path):
    """Bridge to FastAPI Emotion Analysis"""
    try:
        import requests
        clean_path = relative_path.replace('/data/', '', 1)
        abs_path = str(DATA_DIR / clean_path)
        
        print(f"🎭 Running Emotion Analysis on: {abs_path}")
        response = requests.get(f"{BACKEND_URL}/analyze/face/emotion?file_path={abs_path}")
        return response.json()
    except Exception as e:
        print(f"❌ Emotion API Error: {e}")
        return {'success': False, 'message': str(e)}

@eel.expose
def run_facial_analysis(relative_path, module_type="pipeline"):
    """Bridge to FastAPI Facial Analysis (gaze, pose, touch, etc)"""
    try:
        import requests
        clean_path = relative_path.replace('/data/', '', 1)
        abs_path = str(DATA_DIR / clean_path)
        
        if module_type == "lips":
            module_type = "lipjaw"
            
        print(f"👁️ Running Face Analysis ({module_type}) on: {abs_path}")
        
        if module_type and module_type not in ("pipeline", "full", "combined"):
            endpoint = f"{BACKEND_URL}/analyze/face/{module_type}?file_path={abs_path}"
        else:
            endpoint = f"{BACKEND_URL}/analyze/face?file_path={abs_path}"
            
        response = requests.get(endpoint)
        return response.json()
    except Exception as e:
        print(f"❌ Facial API Error: {e}")
        return {'success': False, 'message': str(e)}

@eel.expose
def run_full_pipeline(relative_path):
    """Bridge to Full Deception Pipeline"""
    try:
        import requests
        clean_path = relative_path.replace('/data/', '', 1)
        abs_path = str(DATA_DIR / clean_path)
        
        print(f"⚙️ Running Full Pipeline on: {abs_path}")
        response = requests.get(f"{BACKEND_URL}/analyze/pipeline?file_path={abs_path}")
        return response.json()
    except Exception as e:
        print(f"❌ Pipeline API Error: {e}")
        return {'success': False, 'message': str(e)}

@eel.expose
def save_analysis_report(report_data):
    """Save analysis results as a persistent report"""
    if not current_user:
        return {'success': False, 'message': 'Not logged in'}
    return database.save_report(current_user['username'], report_data)

@eel.expose
def get_reports():
    """Get user's saved reports"""
    if not current_user:
        return response(success=False, message="Not logged in")
    try:
        data = database.get_user_reports(current_user['username'])
        # Sort by timestamp descending
        data.sort(key=lambda x: x.get('analysis_date', x.get('timestamp', '')), reverse=True)
        return response(data=data)
    except Exception as e:
        return response(success=False, message=str(e))

@eel.expose
def delete_report(report_id):
    """Delete a specific forensic report"""
    if not current_user:
        return response(success=False, message="Not logged in")
    try:
        return database.delete_report(report_id, current_user['username'])
    except Exception as e:
        return response(success=False, message=str(e))

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
