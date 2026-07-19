import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".deceptron"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_FILE = Path(__file__).resolve().parent / ".env"

DEFAULT_CONFIG = {
    "backend_host": "localhost",
    "backend_port": 8000,
    "backend_protocol": "http",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "",
    "smtp_pass": ""
}

def _load_env():
    """Load SMTP credentials from .env file if it exists."""
    env_cfg = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            env_cfg[key.strip()] = val.strip()
    return {
        "smtp_host": env_cfg.get("SMTP_HOST", DEFAULT_CONFIG["smtp_host"]),
        "smtp_port": int(env_cfg.get("SMTP_PORT", DEFAULT_CONFIG["smtp_port"])),
        "smtp_user": env_cfg.get("SMTP_USER", ""),
        "smtp_pass": env_cfg.get("SMTP_PASS", "")
    }

def _ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
    return CONFIG_FILE

def load_config():
    _ensure_config()
    env_cfg = _load_env()
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
            merged = {**DEFAULT_CONFIG, **cfg, **env_cfg}
            return merged
    except Exception:
        return {**DEFAULT_CONFIG, **env_cfg}

def save_config(updates):
    cfg = load_config()
    cfg.update(updates)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    return cfg

def get_backend_url():
    cfg = load_config()
    return f"{cfg['backend_protocol']}://{cfg['backend_host']}:{cfg['backend_port']}"

def get_smtp_config():
    cfg = load_config()
    return {
        "SMTP_HOST": cfg.get("smtp_host", "smtp.gmail.com"),
        "SMTP_PORT": cfg.get("smtp_port", 587),
        "SMTP_USER": cfg.get("smtp_user", ""),
        "SMTP_PASS": cfg.get("smtp_pass", "")
    }

BACKEND_URL = get_backend_url()
SMTP_CONFIG = get_smtp_config()
