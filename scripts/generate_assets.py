"""Generate UI assets and Kivy theme using Gemini API."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.gemini import get_client, generate_image, generate_text


ASSET_DIR = Path(__file__).parent.parent / "src" / "assets"
THEME_DIR = Path(__file__).parent.parent / "src" / "theme"

UNIT_ICONS = {
    "pozdravi": "A friendly waving hand icon, flat design, vibrant green background, suitable for a language learning app greeting lesson",
    "stevila": "Colorful numbers 1-2-3 icon, flat design, blue background, suitable for a language learning app numbers lesson",
    "barve": "A painter's palette with multiple colors icon, flat design, rainbow tones, suitable for a language learning app colors lesson",
    "hrana": "A plate with bread and apple icon, flat design, warm orange background, suitable for a language learning app food lesson",
    "druzina": "A happy family silhouette icon, flat design, warm pink background, suitable for a language learning app family lesson",
    "zivali": "Cute cartoon cat and dog icon, flat design, green background, suitable for a language learning app animals lesson",
    "telo": "Simple human body outline icon, flat design, light blue background, suitable for a language learning app body parts lesson",
    "oblacila": "T-shirt and pants icon, flat design, purple background, suitable for a language learning app clothing lesson",
    "hisa": "Simple house with a door and window icon, flat design, warm yellow background, suitable for a language learning app house lesson",
    "cas": "A clock icon showing time, flat design, teal background, suitable for a language learning app time lesson",
}

THEME_PROMPT = """Generate a Kivy .kv style file for a language learning app called Slovenčk.

The design should be:
- Friendly and approachable, inspired by Duolingo but with its own identity
- Primary color: a warm green (#58CC02 or similar)
- Secondary color: a soft blue (#1CB0F6 or similar)
- Background: light warm gray (#F7F7F7)
- Error/wrong: soft red (#FF4B4B)
- Correct: bright green (#58CC02)
- Card backgrounds: white (#FFFFFF) with subtle shadow
- Font sizes: title 28sp, body 20sp, button 18sp
- Rounded buttons with padding
- Card-style containers with rounded corners

Output ONLY the .kv file content, no explanation. Use Kivy styling syntax.
Define styles for: Button, Label, BoxLayout (cards), ProgressBar, TextInput.
Use <ClassName@Widget> convention for custom styled widgets like RoundedButton, CardBox, etc.
"""


def main():
    client = get_client()

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    THEME_DIR.mkdir(parents=True, exist_ok=True)

    # Generate app logo
    logo_path = ASSET_DIR / "logo.png"
    if not logo_path.exists():
        print("Generating app logo...")
        logo_bytes = generate_image(
            client,
            "A modern app logo for 'Slovenčk', a Slovenian language learning app. "
            "Green and white color scheme, clean flat design, shows a speech bubble with "
            "Slovenian flag colors (white-blue-red). Square icon, no text.",
        )
        logo_path.write_bytes(logo_bytes)
        print(f"  Saved: {logo_path}")

    # Generate background
    bg_path = ASSET_DIR / "background.png"
    if not bg_path.exists():
        print("Generating background texture...")
        bg_bytes = generate_image(
            client,
            "A subtle, light warm gray background texture with faint geometric patterns, "
            "suitable for a mobile language learning app. Minimal, clean, not distracting.",
        )
        bg_path.write_bytes(bg_bytes)
        print(f"  Saved: {bg_path}")

    # Generate completion badge
    badge_path = ASSET_DIR / "badge_complete.png"
    if not badge_path.exists():
        print("Generating completion badge...")
        badge_bytes = generate_image(
            client,
            "A golden star completion badge icon, flat design, celebratory, "
            "suitable for a language learning app achievement. Clean, simple, no text.",
        )
        badge_path.write_bytes(badge_bytes)
        print(f"  Saved: {badge_path}")

    # Generate unit icons
    for unit_id, prompt in UNIT_ICONS.items():
        icon_path = ASSET_DIR / f"icon_{unit_id}.png"
        if icon_path.exists():
            print(f"  Skipping (exists): {icon_path}")
            continue
        print(f"Generating icon for {unit_id}...")
        try:
            icon_bytes = generate_image(client, prompt)
            icon_path.write_bytes(icon_bytes)
            print(f"  Saved: {icon_path}")
        except Exception as e:
            print(f"  ERROR for {unit_id}: {e}")

    # Generate Kivy theme
    theme_path = THEME_DIR / "style.kv"
    if True:  # always regenerate theme
        print("Generating Kivy theme...")
        theme_content = generate_text(client, THEME_PROMPT)
        # Strip markdown code fences if present
        theme_content = theme_content.strip()
        if theme_content.startswith("```"):
            lines = theme_content.split("\n")
            lines = lines[1:]  # remove opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            theme_content = "\n".join(lines)
        theme_path.write_text(theme_content)
        print(f"  Saved: {theme_path}")

    print("\nAsset generation complete!")


if __name__ == "__main__":
    main()
