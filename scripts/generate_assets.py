"""Generate UI assets and Kivy theme using Gemini API."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.gemini import get_client, generate_image, generate_text


ASSET_DIR = Path(__file__).parent.parent / "src" / "assets"
THEME_DIR = Path(__file__).parent.parent / "src" / "theme"

STYLE = (
    "Minimalist line-art symbol on a plain muted earthy background. "
    "Warm tones: terracotta, sand, olive, clay, sage. "
    "Thin elegant strokes, no cartoon style, no childish elements. "
    "Sophisticated, adult aesthetic. Simple, clean, no text, no gradients. "
    "Single icon centered on solid warm-toned background, square aspect ratio."
)

UNIT_ICONS = {
    "pozdravi": f"A single minimalist open hand symbol, thin line art. {STYLE}",
    "stevila": f"A minimalist '123' typographic symbol, thin serif font. {STYLE}",
    "barve": f"Three overlapping circles in muted earthy tones, minimalist. {STYLE}",
    "hrana": f"A minimalist wheat stalk or bread loaf line drawing. {STYLE}",
    "druzina": f"Two or three simple abstract human figures, thin lines. {STYLE}",
    "zivali": f"A minimalist fox or bird silhouette, single elegant line. {STYLE}",
    "telo": f"A minimalist abstract human figure outline, da Vinci inspired. {STYLE}",
    "oblacila": f"A minimalist hanger or coat silhouette, single thin line. {STYLE}",
    "hisa": f"A minimalist house outline, geometric, single thin line. {STYLE}",
    "cas": f"A minimalist sundial or clock face, thin elegant lines. {STYLE}",
}


def main():
    client = get_client()

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    THEME_DIR.mkdir(parents=True, exist_ok=True)

    # Generate app logo
    logo_path = ASSET_DIR / "logo.png"
    if not logo_path.exists():
        print("Generating app logo...")
        try:
            logo_bytes = generate_image(
                client,
                "A minimalist app logo for a Slovenian language app. "
                "An abstract speech bubble formed by a single elegant line, "
                "warm terracotta and sand color palette. "
                "Sophisticated, adult, no text. Square, clean background.",
            )
            logo_path.write_bytes(logo_bytes)
            print(f"  Saved: {logo_path}")
        except Exception as e:
            print(f"  ERROR: {e}")

    # Generate completion badge
    badge_path = ASSET_DIR / "badge_complete.png"
    if not badge_path.exists():
        print("Generating completion badge...")
        try:
            badge_bytes = generate_image(
                client,
                "A minimalist checkmark inside a circle, thin elegant line art. "
                "Warm olive green on sand/cream background. Sophisticated, no text, "
                "no cartoon style. Square aspect ratio.",
            )
            badge_path.write_bytes(badge_bytes)
            print(f"  Saved: {badge_path}")
        except Exception as e:
            print(f"  ERROR: {e}")

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

    print("\nAsset generation complete!")


if __name__ == "__main__":
    main()
