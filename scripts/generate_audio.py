"""Generate TTS audio files for all Slovenian text in the curriculum using Gemini TTS."""
import hashlib
import sys
import os
import wave
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from google import genai
from google.genai import types
from services.curriculum import CurriculumLoader


def audio_path(text: str, output_dir: Path) -> Path:
    h = hashlib.md5(text.encode()).hexdigest()
    return output_dir / f"{h}.wav"


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GEMINI_API_KEY environment variable")
        return

    client = genai.Client(api_key=api_key)
    output_dir = Path(__file__).parent.parent / "src" / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)

    loader = CurriculumLoader()
    texts = loader.get_all_slovenian_texts()

    print(f"Generating audio for {len(texts)} Slovenian texts...")
    generated = 0
    skipped = 0
    errors = 0

    for text in texts:
        path = audio_path(text, output_dir)
        if path.exists():
            skipped += 1
            continue
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=f"Say this Slovenian text clearly and naturally: {text}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                        )
                    ),
                ),
            )
            # Extract audio data
            audio_data = response.candidates[0].content.parts[0].inline_data.data
            # Write as WAV (Gemini returns raw PCM at 24kHz)
            with wave.open(str(path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(24000)
                wf.writeframes(audio_data)
            generated += 1
            if generated % 10 == 0:
                print(f"  Generated {generated} files...")
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ERROR for '{text}': {e}")
            elif errors == 6:
                print(f"  (suppressing further errors...)")

    print(f"\nDone. Generated: {generated}, Skipped: {skipped}, Errors: {errors}")


if __name__ == "__main__":
    main()
