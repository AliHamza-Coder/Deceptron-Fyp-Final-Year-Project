import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".deceptron"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "backend_host": "localhost",
    "backend_port": 8000,
    "backend_protocol": "http"
}

def _ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
    return CONFIG_FILE

def load_config():
    _ensure_config()
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
            return {**DEFAULT_CONFIG, **cfg}
    except Exception:
        return dict(DEFAULT_CONFIG)

def save_config(updates):
    cfg = load_config()
    cfg.update(updates)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    return cfg

def get_backend_url():
    cfg = load_config()
    return f"{cfg['backend_protocol']}://{cfg['backend_host']}:{cfg['backend_port']}"

BACKEND_URL = get_backend_url()
