document.addEventListener('DOMContentLoaded', () => {
    const savedEmail = sessionStorage.getItem('reset_email');
    if (savedEmail) {
        document.getElementById('resetEmail').value = savedEmail;
    }
});

document.getElementById('resetForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('resetEmail').value.trim();
    const code = document.getElementById('resetCode').value.trim();
    const newPwd = document.getElementById('newPwd').value;
    const confirmPwd = document.getElementById('confirmPwd').value;
    const btn = document.getElementById('resetBtn');

    let valid = true;

    if (!code || code.length !== 6) {
        document.getElementById('codeError').classList.add('visible');
        document.getElementById('resetCode').classList.add('input-error');
        valid = false;
    } else {
        document.getElementById('codeError').classList.remove('visible');
        document.getElementById('resetCode').classList.remove('input-error');
    }

    if (newPwd.length < 6) {
        document.getElementById('pwdError').classList.add('visible');
        document.getElementById('newPwd').classList.add('input-error');
        valid = false;
    } else {
        document.getElementById('pwdError').classList.remove('visible');
        document.getElementById('newPwd').classList.remove('input-error');
    }

    if (newPwd !== confirmPwd) {
        document.getElementById('confirmError').classList.add('visible');
        document.getElementById('confirmPwd').classList.add('input-error');
        valid = false;
    } else {
        document.getElementById('confirmError').classList.remove('visible');
        document.getElementById('confirmPwd').classList.remove('input-error');
    }

    if (!valid) return;

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Resetting...';

    try {
        const result = await eel.reset_password(email, code, newPwd)();
        if (result.success) {
            btn.classList.add('btn-success');
            btn.innerHTML = '<i class="fas fa-check"></i> Password Reset!';
            sessionStorage.removeItem('reset_email');
            setTimeout(() => {
                alert('Password reset successfully! Please sign in.');
                window.location.href = 'login.html';
            }, 800);
        } else {
            alert('Error: ' + result.message);
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sync-alt"></i> Reset Password';
        }
    } catch (err) {
        console.error('Reset password error:', err);
        alert('An error occurred: ' + err.message);
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Reset Password';
    }
});

document.getElementById('resetCode').addEventListener('input', function() {
    this.value = this.value.replace(/\D/g, '').slice(0, 6);
});
