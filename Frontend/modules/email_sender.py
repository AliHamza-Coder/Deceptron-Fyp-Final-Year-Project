import smtplib
import ssl
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "email_templates"
LOGO_PATH = BASE_DIR.parent / "web" / "assets" / "images" / "Logo2.png"


def check_internet():
    try:
        socket.create_connection(("smtp.gmail.com", 587), timeout=5)
        return True
    except (OSError, socket.timeout):
        return False


class EmailSender:
    def __init__(self, config: dict):
        self.host = config.get("SMTP_HOST", "smtp.gmail.com")
        self.port = int(config.get("SMTP_PORT", 587))
        self.user = config.get("SMTP_USER", "")
        self.passw = config.get("SMTP_PASS", "")

    def _send(self, to_email: str, subject: str, html: str, embed_logo=True):
        if not self.user or not self.passw:
            raise RuntimeError("SMTP credentials missing. Set SMTP_USER and SMTP_PASS in .env")
        msg = MIMEMultipart("related")
        msg["From"] = self.user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html"))
        if embed_logo and LOGO_PATH.exists():
            with open(LOGO_PATH, "rb") as f:
                img = MIMEImage(f.read())
                img.add_header("Content-ID", "<logo>")
                img.add_header("Content-Disposition", "inline")
                msg.attach(img)
        ctx = ssl.create_default_context()
        with smtplib.SMTP(self.host, self.port, timeout=15) as server:
            server.starttls(context=ctx)
            server.login(self.user, self.passw)
            server.sendmail(self.user, to_email, msg.as_string())

    def send_verification(self, email: str, code: str):
        html = (TEMPLATES_DIR / "verify.html").read_text(encoding="utf-8")
        html = html.replace("{{CODE}}", code)
        self._send(email, "Verify your Deceptron account", html, embed_logo=True)

    def send_welcome(self, email: str, name: str):
        html = (TEMPLATES_DIR / "welcome.html").read_text(encoding="utf-8")
        html = html.replace("{{NAME}}", name)
        self._send(email, f"Welcome to Deceptron, {name}!", html, embed_logo=True)

    def send_reset_code(self, email: str, code: str):
        html = (TEMPLATES_DIR / "reset_password.html").read_text(encoding="utf-8")
        html = html.replace("{{CODE}}", code)
        self._send(email, "Deceptron Password Reset", html, embed_logo=True)
