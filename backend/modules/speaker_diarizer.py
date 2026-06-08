"""
speaker_diarizer.py

Speaker diarization module – identifies WHO spoke WHEN.
Uses pyannote.audio pretrained pipeline.

Class:
    SpeakerDiarizer
        diarize(audio_path) -> list of dicts
"""

import os
import json
import torch
from pyannote.audio import Pipeline


class SpeakerDiarizer:
    """Splits an audio file into speaker‑labelled segments."""

    def __init__(self, device="cpu"):
        """Initialize the diarization pipeline for 100% OFFLINE use.

        Args:
            device: 'cpu' or 'cuda'.
        """
        self.device = torch.device(device)
        
        # Resolve base directory (Handles PyInstaller .exe mode)
        import sys
        from pathlib import Path
        if getattr(sys, 'frozen', False):
            # Prioritize internal bundled models for portability
            base_dir = Path(sys._MEIPASS)
        else:
            base_dir = Path(__file__).resolve().parent.parent
            
        local_config = base_dir / "myenv" / "local_models" / "diarizer" / "config.yaml"
        
        # Fallback to external directory if not found inside EXE
        if not local_config.exists() and getattr(sys, 'frozen', False):
            local_config = Path(sys.executable).parent / "myenv" / "local_models" / "diarizer" / "config.yaml"
        
        if not local_config.exists():
            raise FileNotFoundError(
                f"Local models not found at {local_config}. "
                "Ensure models are bundled or placed in 'myenv/local_models' next to the EXE."
            )
            
        try:
            print(f"Loading Pyannote Diarization from {local_config}...")
            self.pipeline = Pipeline.from_pretrained(str(local_config))
            self.pipeline.to(self.device)
            print("Pyannote loaded successfully.")
        except Exception as e:
            print(f"Could not load offline diarization pipeline: {e}")
            raise

    def diarize(self, audio_path):
        """Run diarization on a WAV file and return segments.

        Returns:
            list of dicts: [
                {'start': float, 'end': float, 'speaker': str},
                ...
            ]
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"Running speaker diarization on {audio_path}...")
        diarization = self.pipeline(audio_path)
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                'start': round(turn.start, 2),
                'end': round(turn.end, 2),
                'speaker': speaker
            })
        print(f"Found {len(segments)} speaker segments.")
        return segments


# ---------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------
if __name__ == "__main__":
    d = SpeakerDiarizer()
    segs = d.diarize("sample_audio.wav")
    for s in segs:
        print(f"[{s['start']:.2f} - {s['end']:.2f}] {s['speaker']}")