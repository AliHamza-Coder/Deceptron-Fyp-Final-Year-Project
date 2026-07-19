from pathlib import Path
from tinydb import TinyDB, Query
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets
import random
import string

DB_DIR = Path.home() / ".deceptron"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = str(DB_DIR / 'db.json')
db = TinyDB(DB_PATH)
users_table = db.table('users')
uploads_table = db.table('uploads')
reports_table = db.table('reports')
pending_table = db.table('pending_signups')

CODE_EXPIRY_MINUTES = 30

def _hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${h}"

def _verify_password(password, stored):
    if '$' not in stored:
        return stored == password
    salt, h = stored.split('$', 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == h

def _generate_code():
    return ''.join(random.choices(string.digits, k=6))

def _expiry():
    return (datetime.now() + timedelta(minutes=CODE_EXPIRY_MINUTES)).isoformat()

def _is_expired(expiry_str):
    if not expiry_str:
        return True
    return datetime.fromisoformat(expiry_str) < datetime.now()

def signup_user(user_data):
    User = Query()
    result = users_table.search((User.email == user_data['email']) | (User.username == user_data['username']))
    if result:
        existing = result[0]
        if existing.get('email') == user_data['email']:
             return {'success': False, 'message': 'Email already registered'}
        if existing.get('username') == user_data['username']:
             return {'success': False, 'message': 'Username already taken'}
    user_data['password'] = _hash_password(user_data['password'])
    user_data['verified'] = True
    users_table.insert(user_data)
    return {'success': True, 'message': 'User registered successfully'}

def _check_duplicate(email, username):
    User = Query()
    result = users_table.search((User.email == email) | (User.username == username))
    if result:
        existing = result[0]
        if existing.get('email') == email:
            return 'Email already registered'
        if existing.get('username') == username:
            return 'Username already taken'
    Pending = Query()
    pending = pending_table.search((Pending.email == email) | (Pending.username == username))
    if pending:
        p = pending[0]
        if p.get('email') == email:
            return 'Email already registered'
        if p.get('username') == username:
            return 'Username already taken'
    return None

def create_pending_signup(user_data):
    dup = _check_duplicate(user_data['email'], user_data['username'])
    if dup:
        return {'success': False, 'message': dup}
    code = _generate_code()
    expiry = _expiry()
    entry = {
        'email': user_data['email'],
        'username': user_data['username'],
        'data': {
            'firstName': user_data.get('firstName', ''),
            'lastName': user_data.get('lastName', ''),
            'username': user_data['username'],
            'email': user_data['email'],
            'password': _hash_password(user_data['password']),
            'created_at': user_data.get('created_at', datetime.now().isoformat())
        },
        'verification_code': code,
        'verification_expiry': expiry,
        'created': datetime.now().isoformat()
    }
    pending_table.insert(entry)
    return {'success': True, 'email': user_data['email'], 'code': code}

def verify_pending_signup(email, code):
    Pending = Query()
    pending = pending_table.get(Pending.email == email)
    if not pending:
        return {'success': False, 'message': 'No pending registration found for this email'}
    stored = pending.get('verification_code')
    expiry = pending.get('verification_expiry')
    if not stored or stored != code:
        return {'success': False, 'message': 'Invalid verification code'}
    if _is_expired(expiry):
        return {'success': False, 'message': 'Verification code expired. Request a new one.'}
    user_data = pending['data']
    user_data['verified'] = True
    users_table.insert(user_data)
    pending_table.remove(doc_ids=[pending.doc_id])
    return {'success': True, 'user': {k: v for k, v in user_data.items() if k != 'password'}}

def resend_pending_code(email):
    Pending = Query()
    pending = pending_table.get(Pending.email == email)
    if not pending:
        return {'success': False, 'message': 'No pending registration found'}
    code = _generate_code()
    pending_table.update({'verification_code': code, 'verification_expiry': _expiry()}, Pending.email == email)
    return {'success': True, 'code': code}

def clean_expired_pending():
    Pending = Query()
    all_pending = pending_table.all()
    for p in all_pending:
        if _is_expired(p.get('verification_expiry')):
            pending_table.remove(doc_ids=[p.doc_id])

def login_user(identity, password):
    User = Query()
    result = users_table.search((User.email == identity) | (User.username == identity))
    if result:
        user = result[0]
        if not user.get('verified', False):
            return {'success': False, 'message': 'Please verify your email first. Check your inbox.', 'needs_verification': True, 'email': user.get('email')}
        if _verify_password(password, user['password']):
            return {'success': True, 'user': {k: v for k, v in user.items() if k != 'password'}}
    return {'success': False, 'message': 'Invalid credentials'}

def get_user_by_email(email):
    User = Query()
    user = users_table.get(User.email == email)
    if user:
        return {'success': True, 'email': email, 'name': user.get('firstName', '')}
    return {'success': False, 'message': 'No account found with that email'}

def set_reset_code(email):
    User = Query()
    user = users_table.get(User.email == email)
    if not user:
        return {'success': False, 'message': 'User not found'}
    code = _generate_code()
    users_table.update({'reset_code': code, 'reset_expiry': _expiry()}, User.email == email)
    return {'success': True, 'code': code}

def verify_reset_code(email, code):
    User = Query()
    user = users_table.get(User.email == email)
    if not user:
        return {'success': False, 'message': 'User not found'}
    stored = user.get('reset_code')
    expiry = user.get('reset_expiry')
    if not stored or stored != code:
        return {'success': False, 'message': 'Invalid reset code'}
    if _is_expired(expiry):
        return {'success': False, 'message': 'Reset code expired. Request a new one.'}
    return {'success': True}

def reset_password(email, code, new_password):
    User = Query()
    user = users_table.get(User.email == email)
    if not user:
        return {'success': False, 'message': 'User not found'}
    stored = user.get('reset_code')
    expiry = user.get('reset_expiry')
    if not stored or stored != code:
        return {'success': False, 'message': 'Invalid reset code'}
    if _is_expired(expiry):
        return {'success': False, 'message': 'Reset code expired. Request a new one.'}
    users_table.update({
        'password': _hash_password(new_password),
        'reset_code': None,
        'reset_expiry': None
    }, User.email == email)
    return {'success': True}

def add_upload(username, file_name, file_type, file_size, file_path=""):
    upload_data = {
        'id': str(uuid.uuid4()),
        'username': username,
        'filename': file_name,
        'type': file_type,
        'size': file_size,
        'filepath': file_path,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    uploads_table.insert(upload_data)
    return {'success': True, 'data': upload_data}

def get_user_uploads(username):
    Upload = Query()
    return uploads_table.search(Upload.username == username)

def delete_upload(upload_id, username):
    Upload = Query()
    item = uploads_table.get((Upload.id == upload_id) & (Upload.username == username))
    if item:
        uploads_table.remove(doc_ids=[item.doc_id])
        return {'success': True, 'data': item}
    return {'success': False, 'message': 'Record not found or access denied'}

def update_user_profile(username, new_data):
    User = Query()
    users_table.update(new_data, User.username == username)
    updated_user = users_table.search(User.username == username)[0]
    return {'success': True, 'user': {k: v for k, v in updated_user.items() if k != 'password'}}

def change_password(username, current_pwd, new_pwd):
    User = Query()
    user = users_table.get(User.username == username)
    if user and _verify_password(current_pwd, user['password']):
        users_table.update({'password': _hash_password(new_pwd)}, User.username == username)
        return {'success': True}
    return {'success': False, 'message': 'Current password incorrect'}

def update_user_preferences(username, preferences):
    User = Query()
    user = users_table.get(User.username == username)
    if not user:
         return {'success': False, 'message': 'User not found'}
    current_prefs = user.get('preferences') or {}
    updated_prefs = {**(current_prefs if isinstance(current_prefs, dict) else {}), **preferences}
    users_table.update({'preferences': updated_prefs}, User.username == username)
    return {'success': True, 'preferences': updated_prefs}

def get_user_preferences(username):
    User = Query()
    user = users_table.get(User.username == username)
    if user:
        return {'success': True, 'preferences': user.get('preferences', {})}
    return {'success': False, 'message': 'User not found'}

def update_last_login(username):
    User = Query()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    users_table.update({'last_login': timestamp}, User.username == username)
    return {'success': True, 'timestamp': timestamp}

def save_report(username, report_data):
    report_data['id'] = str(uuid.uuid4())
    report_data['username'] = username
    report_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reports_table.insert(report_data)
    return {'success': True, 'data': report_data}

def get_user_reports(username):
    Report = Query()
    return reports_table.search(Report.username == username)

def get_report_by_id(report_id, username):
    Report = Query()
    return reports_table.get((Report.id == report_id) & (Report.username == username))

def delete_report(report_id, username):
    Report = Query()
    item = reports_table.get((Report.id == report_id) & (Report.username == username))
    if item:
        reports_table.remove(doc_ids=[item.doc_id])
        return {'success': True}
    return {'success': False, 'message': 'Report not found'}
