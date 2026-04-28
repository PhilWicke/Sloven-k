import hashlib
from pathlib import Path

AUDIO_DIR = Path(__file__).parent.parent / "audio"


def get_audio_path(text: str) -> str:
    h = hashlib.md5(text.encode()).hexdigest()
    path = AUDIO_DIR / f"{h}.mp3"
    return str(path) if path.exists() else ""


def play_audio(text: str):
    """Play audio for the given Slovenian text. No-op if file missing or Kivy unavailable."""
    path = get_audio_path(text)
    if not path:
        return
    try:
        from kivy.core.audio import SoundLoader
        sound = SoundLoader.load(path)
        if sound:
            sound.play()
    except Exception:
        pass  # audio is optional, don't crash
