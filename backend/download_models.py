import os
import sys
import yaml
from pathlib import Path

try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("huggingface_hub not found. Please run: pip install huggingface_hub")
    sys.exit(1)

def download_and_patch_models():
    print("=== Deceptron Offline Model Downloader ===")
    print("This script will download all required AI models so your app can run 100% OFFLINE.\n")

    # 1. Setup paths inside myenv
    current_dir = Path(__file__).resolve().parent
    models_dir = current_dir / "myenv" / "local_models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Target Directory: {models_dir}")

    # 2. Get token
    token = input("Enter your Hugging Face Token (starts with hf_): ").strip()
    if not token:
        print("Error: A token is required for the one-time download.")
        sys.exit(1)

    # 3. Download Models
    jobs = [
        {"repo": "pyannote/speaker-diarization-3.1", "folder": "diarizer"},
        {"repo": "pyannote/segmentation-3.0", "folder": "segmenter"},
        {"repo": "pyannote/wespeaker-voxceleb-resnet34-LM", "folder": "embedding"}
    ]
    
    local_paths = {}
    for job in jobs:
        repo_id = job["repo"]
        local_folder = models_dir / job["folder"]
        local_paths[job["folder"]] = local_folder
        print(f"\n--- Downloading {repo_id} ---")
        try:
            snapshot_download(
                repo_id=repo_id,
                token=token,
                local_dir=str(local_folder),
                local_dir_use_symlinks=False 
            )
            print(f"Successfully downloaded to {local_folder.name}")
        except Exception as e:
            print(f"Error downloading {repo_id}: {e}")
            print("\nDid you accept the license on Hugging Face?")
            print(f"URL: https://huggingface.co/{repo_id}")
            sys.exit(1)

    # 4. Patch config.yaml for 100% offline use
    print("\n--- Patching configurations for OFFLINE mode ---")
    config_path = local_paths["diarizer"] / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Point to absolute local paths
            config['pipeline']['params']['segmentation'] = str(local_paths["segmenter"] / "pytorch_model.bin")
            config['pipeline']['params']['embedding'] = str(local_paths["embedding"] / "pytorch_model.bin")
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
            print("[OK] diarizer config.yaml updated successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to patch config.yaml: {e}")
    else:
        print("[ERROR] diarizer/config.yaml not found!")

    # 5. Download Whisper
    print("\n--- Downloading Whisper 'base' model ---")
    try:
        import whisper
        whisper_dir = models_dir / "whisper"
        whisper.load_model("base", download_root=str(whisper_dir))
        print(f"[OK] Whisper saved in: {whisper_dir}")
    except Exception as e:
        print(f"[ERROR] Whisper download failed: {e}")

    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE! Your app is now 100% OFFLINE capable.")
    print("You can now safely delete your Hugging Face API key from .env.")
    print("="*60)

if __name__ == "__main__":
    download_and_patch_models()
