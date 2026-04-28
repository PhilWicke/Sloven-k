"""Generate UI assets and Kivy theme using Gemini API."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.gemini import get_client, generate_image, generate_text


ASSET_DIR = Path(__file__).parent.parent / "src" / "assets"
THEME_DIR = Path(__file__).parent.parent / "src" / "theme"

STYLE = (
    "Single minimal line-art icon on a solid #E8E0D4 (warm sand) background. "
    "Thin dark brown (#5C4A3A) strokes only, no fills, no shading, no gradients. "
    "Consistent 2px stroke weight. Centered in frame. 64x64px style, "
    "extremely simple — no more than 5-6 strokes. Square aspect ratio. No text."
)

UNIT_ICONS = {
    "pozdravi": f"A single raised open palm. {STYLE}",
    "stevila": f"The numeral 3 in a thin serif. {STYLE}",
    "barve": f"Three overlapping circles. {STYLE}",
    "hrana": f"A simple apple with one leaf. {STYLE}",
    "druzina": f"Two stick figures side by side. {STYLE}",
    "zivali": f"A simple bird in profile. {STYLE}",
    "telo": f"A minimal human silhouette. {STYLE}",
    "oblacila": f"A coat hanger. {STYLE}",
    "hisa": f"A house outline, square plus triangle roof. {STYLE}",
    "cas": f"A circle with two clock hands. {STYLE}",
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
