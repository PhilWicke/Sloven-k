# Slovenčk — Design Spec

**Date:** 2026-04-28
**Status:** Approved

A personal Slovenian language learning app, Duolingo-inspired, built for a single absolute-beginner user.

---

## 1. Architecture

Single-process Kivy application. Python/uv for package management. Runs locally on desktop for testing and builds to Android APK via Buildozer.

```
Slovenčk/
├── pyproject.toml          # uv project config
├── src/
│   ├── main.py             # App entry point
│   ├── screens/            # Kivy screens (home, lesson_select, exercise, results)
│   ├── exercises/          # Exercise type logic (one module per type)
│   ├── data/
│   │   ├── curriculum.json # Lesson definitions, vocab, sentences
│   │   └── progress.json   # Completion + spaced repetition state
│   ├── audio/              # TTS cache (pre-generated .mp3 files)
│   ├── assets/             # Gemini-generated images, icons, backgrounds
│   ├── services/
│   │   ├── tts.py          # Text-to-speech generation for Slovenian
│   │   ├── gemini.py       # Gemini API client for design generation
│   │   └── srs.py          # Spaced repetition algorithm
│   └── theme/              # Gemini-generated Kivy styles/kv files
├── buildozer.spec          # Android build config
└── scripts/
    ├── generate_assets.py  # One-off: generate UI assets via Gemini
    └── generate_audio.py   # One-off: generate TTS audio for all content
```

**Key decisions:**
- All lesson content in `curriculum.json` — no database needed for a single user.
- Progress stored in `progress.json` — lesson completion + per-word SRS data.
- Gemini asset generation is a build-time step (run a script), not runtime — no API calls while using the app.
- TTS audio is pre-generated and cached locally, no network needed during lessons.

---

## 2. Screens & Navigation

Four main screens with stack-based navigation: Home -> Lesson Select -> Exercise -> Results -> back to Lesson Select.

### Home Screen
- Current progress overview (lessons completed, words learned)
- "Continue" button that drops into the next incomplete lesson
- Gemini-generated background/branding

### Lesson Select Screen
- Vertical scrollable list of themed lesson units
- Each unit shows: Slovenian name / English name, completion badge, SRS strength indicator
- Locked lessons greyed out until prerequisites completed

### Exercise Screen
- Loads one exercise at a time from the current lesson
- Progress bar at top showing position within the lesson
- Six exercise types render within this same screen (see Section 4)

### Results Screen
- Score for the completed lesson
- Words flagged for review
- Options: retry lesson or continue to next

---

## 3. Curriculum & Content

### Lesson structure
Each lesson belongs to a themed unit and contains ~10-15 vocabulary items plus a few sentences. A single lesson session pulls ~10 exercises mixing all 6 types, prioritizing words the SRS flags for review.

### Initial units (in order)
1. **Pozdravi / Greetings** — Dober dan, Živjo, Hvala, Prosim...
2. **Števila / Numbers** — 1-20
3. **Barve / Colors** — rdeča, modra, zelena...
4. **Hrana / Food** — kruh, mleko, jabolko...
5. **Družina / Family** — mama, oče, brat, sestra...
6. **Živali / Animals** — pes, mačka, ptica...
7. **Telo / Body** — glava, roka, noga...
8. **Oblačila / Clothing** — majica, hlače, čevlji...
9. **Hiša / House** — kuhinja, soba, miza...
10. **Čas / Time** — danes, jutri, ura...

### Content format in curriculum.json
Each vocab item contains:
- `sl`: Slovenian word
- `en`: English translation
- `gender`: grammatical gender (where applicable)
- `example`: example sentence in Slovenian
- `example_en`: example sentence English translation
- `phonetic`: phonetic hint for pronunciation

Sentences are tagged with difficulty level and which vocabulary items they exercise.

---

## 4. Exercise Types

All six types render within the Exercise Screen:

1. **Flashcard** — Card with word, tap to flip and reveal translation + play audio
2. **Multiple Choice** — Prompt at top, 4 tappable answer buttons
3. **Sentence Building** — Scrambled word tiles, tap in order to build a sentence
4. **Fill-in-the-blank** — Sentence with a gap, word bank to pick from
5. **Listening** — Audio plays automatically, select the correct word/phrase from 4 multiple-choice options
6. **Typing** — See Slovenian word/phrase, type the English translation (or vice versa)

Each exercise provides immediate feedback (correct/incorrect) with the right answer shown on mistakes.

---

## 5. Spaced Repetition & Progress

### SRS algorithm (simplified Leitner boxes)
Five levels:
- **Box 1:** New/failed words — appear every session
- **Box 2:** Reviewed once correctly — appear after 1 day
- **Box 3:** After 3 days
- **Box 4:** After 7 days
- **Box 5:** After 14 days — considered "learned"

Correct answer moves word up a box. Incorrect answer sends word back to Box 1.

### Exercise selection within a lesson
1. Pull in SRS-due words from this lesson's vocab first
2. Fill remaining slots with new unseen words
3. Mix exercise types pseudo-randomly (no two of the same type in a row)

### Progress tracking (progress.json)
- **Per-lesson:** completion status (not_started / in_progress / completed), best score
- **Per-word:** SRS box level, last reviewed date, correct/incorrect counts
- **Overall:** lessons completed, total words learned (reached Box 5)

Loaded at app start, saved after each exercise answer.

---

## 6. Audio (TTS)

- **Library:** gTTS (Google Text-to-Speech), supports Slovenian (`sl` locale)
- **Pre-generation:** `scripts/generate_audio.py` reads all words and sentences from `curriculum.json`, saves `.mp3` files to `src/audio/`, named by hash of the text content
- **Playback:** Kivy's `SoundLoader`, no network needed at runtime
- **Updating:** re-run the generation script after adding new curriculum content

---

## 7. Gemini Integration

Build-time design generation via `scripts/generate_assets.py`:

### Visual assets
- App logo
- Lesson unit icons (one per theme, e.g., food icon for Hrana)
- Background textures
- Completion badges

### Kivy theme
- `.kv` style file defining colors, font sizes, button styles, spacing, card appearance
- Prompted to produce a friendly, Duolingo-inspired but distinct visual identity

### Configuration
- Gemini API key read from environment variable `GEMINI_API_KEY`
- Only needed when running the generation script
- Generated assets committed to repo so regeneration is optional

---

## 8. Android Build & Local Testing

### Local testing
- `uv run python src/main.py` — Kivy opens a desktop window
- Window size fixed to 360x640 to simulate mobile viewport
- Full functionality: exercises, audio playback, progress saving

### Android deployment
- `buildozer.spec` configures APK: app name "Slovenčk", storage permissions, bundled assets
- Buildozer requires Linux — use Docker container on macOS (`docker run buildozer`) or GitHub Actions CI
- APK sideloaded to phone via USB or file transfer
- Progress stored locally on device

### Development workflow
1. Edit code/content -> test locally with `uv run python src/main.py`
2. Regenerate assets if needed: `uv run python scripts/generate_assets.py`
3. Regenerate audio if needed: `uv run python scripts/generate_audio.py`
4. Build APK via Docker/CI -> transfer to phone
