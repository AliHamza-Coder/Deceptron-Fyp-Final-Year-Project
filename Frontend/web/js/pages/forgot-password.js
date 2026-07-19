let lastEmail = '';

document.getElementById('forgotForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('resetEmail').value.trim();
    const btn = document.getElementById('sendCodeBtn');
    const emailError = document.getElementById('emailError');
    const resendSection = document.getElementById('resendSection');

    if (!isValidEmail(email)) {
        emailError.classList.add('visible');
        document.getElementById('resetEmail').classList.add('input-error');
        return;
    }
    emailError.classList.remove('visible');
    document.getElementById('resetEmail').classList.remove('input-error');

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

    try {
        const result = await eel.send_reset_code(email)();
        if (result.success) {
            lastEmail = email;
            document.getElementById('forgotForm').style.display = 'none';
            document.getElementById('successState').classList.remove('hidden');
            sessionStorage.setItem('reset_email', email);
        } else {
            alert(result.message);
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Reset Code';
        }
    } catch (err) {
        console.error('Send reset code error:', err);
        alert('An error occurred: ' + err.message);
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Reset Code';
    }
});

document.getElementById('resendLink').addEventListener('click', async (e) => {
    e.preventDefault();
    const link = e.target;
    if (link.dataset.cooldown === '1') return;

    link.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Resending...';
    link.style.pointerEvents = 'none';

    try {
        const result = await eel.send_reset_code(lastEmail)();
        alert(result.success ? 'Code resent successfully!' : result.message);
    } catch (err) {
        alert('Error resending code: ' + err.message);
    }

    link.innerHTML = 'Resend code';
    link.dataset.cooldown = '1';
    setTimeout(() => {
        link.dataset.cooldown = '0';
        link.style.pointerEvents = 'auto';
    }, 60000);
});

document.getElementById('goToResetBtn').addEventListener('click', (e) => {
    e.preventDefault();
    window.location.href = 'reset-password.html';
});
