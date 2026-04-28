"""Generate TTS audio files for all Slovenian text in the curriculum."""
import hashlib
import sys
from pathlib import Path

# Add src to path so we can import services
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gtts import gTTS
from services.curriculum import CurriculumLoader


def audio_path(text: str, output_dir: Path) -> Path:
    h = hashlib.md5(text.encode()).hexdigest()
    return output_dir / f"{h}.mp3"


def main():
    output_dir = Path(__file__).parent.parent / "src" / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)

    loader = CurriculumLoader()
    texts = loader.get_all_slovenian_texts()

    print(f"Generating audio for {len(texts)} Slovenian texts...")
    generated = 0
    skipped = 0

    for text in texts:
        path = audio_path(text, output_dir)
        if path.exists():
            skipped += 1
            continue
        try:
            tts = gTTS(text=text, lang="sl")
            tts.save(str(path))
            generated += 1
            print(f"  Generated: {text} -> {path.name}")
        except Exception as e:
            print(f"  ERROR for '{text}': {e}")

    print(f"\nDone. Generated: {generated}, Skipped (existing): {skipped}")


if __name__ == "__main__":
    main()
