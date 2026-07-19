let signupEmail = '';

document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerText;

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';

    const fields = e.target.querySelectorAll('input');
    const user_data = {
        firstName: fields[0].value,
        lastName: fields[1].value,
        username: fields[2].value,
        email: fields[3].value,
        password: fields[4].value,
        created_at: new Date().toISOString()
    };

    try {
        if (typeof eel === 'undefined') {
            throw new Error("Eel is not loaded. Please restart the application.");
        }

        const result = await eel.initiate_signup(user_data)();
        if (result.success) {
            signupEmail = user_data.email;
            document.getElementById('signupStep').classList.add('hidden');
            document.getElementById('verifyEmailDisplay').textContent = signupEmail;
            document.getElementById('verifyStep').classList.remove('hidden');

            if (!result.email_sent) {
                const note = document.createElement('div');
                note.style.cssText = 'background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);border-radius:0.75rem;padding:0.75rem 1rem;margin-bottom:1rem;font-size:0.75rem;color:#f59e0b;text-align:center;';
                note.innerHTML = '<i class="fas fa-exclamation-triangle" style="margin-right:6px;"></i> ' + result.message +
                    '<br><span style="font-size:0.7rem;color:#94a3b8;">Click "Resend code" once connected.</span>';
                document.getElementById('verifyStep').insertBefore(note, document.getElementById('verifyStep').querySelector('.form-top').nextSibling);
            }
        } else {
            alert('Error: ' + result.message);
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    } catch (err) {
        console.error('Signup error:', err);
        alert('An error occurred: ' + err.message);
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
});

document.getElementById('verifyBtn').addEventListener('click', async () => {
    const code = document.getElementById('verifyCode').value.trim();
    const errorEl = document.getElementById('verifyCodeError');
    const btn = document.getElementById('verifyBtn');

    if (!code || code.length !== 6) {
        errorEl.classList.add('visible');
        return;
    }
    errorEl.classList.remove('visible');

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';

    try {
        const result = await eel.verify_email(signupEmail, code)();
        if (result.success) {
            btn.innerHTML = '<i class="fas fa-check"></i> Verified!';
            btn.classList.add('btn-success');
            setTimeout(() => {
                alert('Email verified successfully! You can now sign in.');
                window.location.href = 'login.html';
            }, 800);
        } else {
            alert('Verification failed: ' + result.message);
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Verify Email';
        }
    } catch (err) {
        console.error('Verify error:', err);
        alert('An error occurred: ' + err.message);
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-check-circle"></i> Verify Email';
    }
});

document.getElementById('verifyResendLink').addEventListener('click', async (e) => {
    const link = e.target;
    if (link.dataset.cooldown === '1') return;

    link.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Resending...';
    link.style.pointerEvents = 'none';

    try {
        const result = await eel.resend_verification_code(signupEmail)();
        alert(result.success ? 'Code sent! Check your email.' : result.message);
    } catch (err) {
        alert('Error: ' + err.message);
    }

    link.innerHTML = 'Resend code';
    link.dataset.cooldown = '1';
    setTimeout(() => {
        link.dataset.cooldown = '0';
        link.style.pointerEvents = 'auto';
    }, 60000);
});

document.getElementById('verifyCode').addEventListener('input', function() {
    this.value = this.value.replace(/\D/g, '').slice(0, 6);
    if (this.value.length === 6) {
        document.getElementById('verifyCodeError').classList.remove('visible');
    }
});

document.getElementById('verifyCode').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && this.value.length === 6) {
        document.getElementById('verifyBtn').click();
    }
});
