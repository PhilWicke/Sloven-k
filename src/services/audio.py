import hashlib
from pathlib import Path

AUDIO_DIR = Path(__file__).parent.parent / "audio"


def get_audio_path(text: str) -> str:
    h = hashlib.md5(text.encode()).hexdigest()
    for ext in (".wav", ".mp3"):
        path = AUDIO_DIR / f"{h}{ext}"
        if path.exists():
            return str(path)
    return ""


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
