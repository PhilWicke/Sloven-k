import hashlib
from pathlib import Path

AUDIO_DIR = Path(__file__).parent.parent / "audio"

# Keep reference to prevent garbage collection during playback
_current_sound = None


def get_audio_path(text: str) -> str:
    h = hashlib.md5(text.encode()).hexdigest()
    for ext in (".wav", ".mp3"):
        path = AUDIO_DIR / f"{h}{ext}"
        if path.exists():
            return str(path)
    return ""


def play_audio(text: str):
    """Play audio for the given Slovenian text. No-op if file missing."""
    global _current_sound
    path = get_audio_path(text)
    if not path:
        return
    try:
        from kivy.core.audio import SoundLoader
        if _current_sound:
            _current_sound.stop()
        _current_sound = SoundLoader.load(path)
        if _current_sound:
            _current_sound.play()
    except Exception as e:
        print(f"Audio error: {e}")
