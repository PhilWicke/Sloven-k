# Slovenčk Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal Slovenian language learning Kivy app with 6 exercise types, spaced repetition, TTS audio, and Gemini-generated UI — testable locally and deployable to Android.

**Architecture:** Single-process Kivy app. Curriculum and progress stored as JSON files. SRS uses a 5-box Leitner system. TTS audio and Gemini UI assets are pre-generated at build time via scripts. Kivy ScreenManager handles navigation between 4 screens.

**Tech Stack:** Python 3.12+, uv, Kivy 2.3+, gTTS, google-genai, Buildozer

---

## File Structure

```
Slovenčk/
├── pyproject.toml
├── buildozer.spec
├── src/
│   ├── __init__.py
│   ├── main.py                     # App entry point, ScreenManager setup
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── home.py                 # HomeScreen
│   │   ├── lesson_select.py        # LessonSelectScreen
│   │   ├── exercise.py             # ExerciseScreen (renders all 6 types)
│   │   └── results.py              # ResultsScreen
│   ├── exercises/
│   │   ├── __init__.py
│   │   ├── base.py                 # ExerciseBase dataclass + check_answer interface
│   │   ├── flashcard.py            # FlashcardExercise
│   │   ├── multiple_choice.py      # MultipleChoiceExercise
│   │   ├── sentence_building.py    # SentenceBuildingExercise
│   │   ├── fill_blank.py           # FillBlankExercise
│   │   ├── listening.py            # ListeningExercise
│   │   ├── typing_ex.py            # TypingExercise
│   │   └── session.py              # SessionBuilder — picks exercises for a lesson
│   ├── services/
│   │   ├── __init__.py
│   │   ├── srs.py                  # Leitner box SRS algorithm
│   │   ├── progress.py             # Load/save progress.json
│   │   ├── curriculum.py           # Load/query curriculum.json
│   │   └── audio.py                # Audio playback helper (wraps SoundLoader)
│   ├── data/
│   │   ├── curriculum.json         # All lesson content
│   │   └── progress.json           # User progress (created at runtime)
│   ├── audio/                      # Pre-generated TTS .mp3 files
│   ├── assets/                     # Gemini-generated images
│   └── theme/
│       └── style.kv                # Kivy styling
├── scripts/
│   ├── generate_audio.py           # gTTS audio generation
│   └── generate_assets.py          # Gemini asset generation
└── tests/
    ├── __init__.py
    ├── test_srs.py
    ├── test_progress.py
    ├── test_curriculum.py
    ├── test_exercises.py
    └── test_session.py
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: all `__init__.py` files
- Create: directory structure

- [ ] **Step 1: Initialize uv project**

```bash
cd ~/Desktop/Slovenčk
uv init --name slovencek --python 3.12
```

- [ ] **Step 2: Replace pyproject.toml with full config**

```toml
[project]
name = "slovencek"
version = "0.1.0"
description = "Personal Slovenian language learning app"
requires-python = ">=3.12"
dependencies = [
    "kivy>=2.3.0",
    "gtts>=2.5.0",
    "google-genai>=1.0.0",
    "pillow>=10.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "buildozer>=1.5.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 3: Create directory structure**

```bash
cd ~/Desktop/Slovenčk
mkdir -p src/screens src/exercises src/services src/data src/audio src/assets src/theme
mkdir -p scripts tests
touch src/__init__.py src/screens/__init__.py src/exercises/__init__.py src/services/__init__.py tests/__init__.py
```

- [ ] **Step 4: Install dependencies**

```bash
cd ~/Desktop/Slovenčk
uv sync
```

- [ ] **Step 5: Verify pytest runs**

```bash
cd ~/Desktop/Slovenčk
uv run pytest --co
```

Expected: no errors, no tests collected yet.

- [ ] **Step 6: Commit**

```bash
cd ~/Desktop/Slovenčk
git add pyproject.toml uv.lock src/ scripts/ tests/
git commit -m "feat: scaffold project structure with uv and dependencies"
```

---

### Task 2: Curriculum Data & Loader

**Files:**
- Create: `src/data/curriculum.json`
- Create: `src/services/curriculum.py`
- Create: `tests/test_curriculum.py`

- [ ] **Step 1: Write the curriculum loader tests**

```python
# tests/test_curriculum.py
import pytest
from services.curriculum import CurriculumLoader


@pytest.fixture
def loader():
    return CurriculumLoader()


def test_load_returns_units(loader):
    units = loader.get_units()
    assert len(units) == 10
    assert units[0]["id"] == "pozdravi"
    assert units[0]["name_sl"] == "Pozdravi"
    assert units[0]["name_en"] == "Greetings"


def test_get_unit_vocab(loader):
    vocab = loader.get_vocab("pozdravi")
    assert len(vocab) >= 10
    first = vocab[0]
    assert "sl" in first
    assert "en" in first
    assert "phonetic" in first
    assert "example" in first
    assert "example_en" in first


def test_get_unit_vocab_invalid_unit(loader):
    with pytest.raises(KeyError):
        loader.get_vocab("nonexistent")


def test_get_sentences(loader):
    sentences = loader.get_sentences("pozdravi")
    assert len(sentences) >= 2
    first = sentences[0]
    assert "sl" in first
    assert "en" in first
    assert "vocab_ids" in first


def test_all_units_have_vocab(loader):
    for unit in loader.get_units():
        vocab = loader.get_vocab(unit["id"])
        assert len(vocab) >= 5, f"Unit {unit['id']} has fewer than 5 vocab items"


def test_get_all_text_for_tts(loader):
    texts = loader.get_all_slovenian_texts()
    assert len(texts) > 50  # at least 50 unique Slovenian strings
    assert all(isinstance(t, str) for t in texts)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/Desktop/Slovenčk
uv run pytest tests/test_curriculum.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'services.curriculum'`

- [ ] **Step 3: Create curriculum.json with all 10 units**

Create `src/data/curriculum.json` with the full curriculum. Each unit has an `id`, `name_sl`, `name_en`, `order`, `vocab` array, and `sentences` array.

The vocab for each unit must contain 10-15 items. Each vocab item: `{"sl": "...", "en": "...", "gender": "m/f/n/null", "phonetic": "...", "example": "...", "example_en": "..."}`.

Each unit has 3-5 sentences: `{"sl": "...", "en": "...", "difficulty": 1, "vocab_ids": ["word1", "word2"]}`.

**Unit 1 — Pozdravi / Greetings (sample, all units follow this pattern):**

```json
{
  "units": [
    {
      "id": "pozdravi",
      "name_sl": "Pozdravi",
      "name_en": "Greetings",
      "order": 1,
      "vocab": [
        {"sl": "dober dan", "en": "good day", "gender": null, "phonetic": "DOH-ber dahn", "example": "Dober dan, kako ste?", "example_en": "Good day, how are you?"},
        {"sl": "živjo", "en": "hello", "gender": null, "phonetic": "ZHEE-vyo", "example": "Živjo, kako si?", "example_en": "Hello, how are you?"},
        {"sl": "hvala", "en": "thank you", "gender": null, "phonetic": "HVAH-lah", "example": "Hvala za pomoč.", "example_en": "Thank you for the help."},
        {"sl": "prosim", "en": "please / you're welcome", "gender": null, "phonetic": "PROH-seem", "example": "Prosim, pomagajte mi.", "example_en": "Please, help me."},
        {"sl": "da", "en": "yes", "gender": null, "phonetic": "dah", "example": "Da, razumem.", "example_en": "Yes, I understand."},
        {"sl": "ne", "en": "no", "gender": null, "phonetic": "neh", "example": "Ne, hvala.", "example_en": "No, thank you."},
        {"sl": "dobro jutro", "en": "good morning", "gender": null, "phonetic": "DOH-broh YOO-troh", "example": "Dobro jutro, kako ste spali?", "example_en": "Good morning, how did you sleep?"},
        {"sl": "dober večer", "en": "good evening", "gender": null, "phonetic": "DOH-ber VEH-cher", "example": "Dober večer, gospod.", "example_en": "Good evening, sir."},
        {"sl": "lahko noč", "en": "good night", "gender": null, "phonetic": "LAH-koh nohch", "example": "Lahko noč, spi dobro.", "example_en": "Good night, sleep well."},
        {"sl": "nasvidenje", "en": "goodbye", "gender": null, "phonetic": "nahs-VEE-den-yeh", "example": "Nasvidenje, se vidimo jutri.", "example_en": "Goodbye, see you tomorrow."},
        {"sl": "oprostite", "en": "excuse me / sorry", "gender": null, "phonetic": "oh-prohs-TEE-teh", "example": "Oprostite, kje je postaja?", "example_en": "Excuse me, where is the station?"},
        {"sl": "kako ste", "en": "how are you (formal)", "gender": null, "phonetic": "KAH-koh steh", "example": "Dober dan, kako ste?", "example_en": "Good day, how are you?"}
      ],
      "sentences": [
        {"sl": "Dober dan, kako ste?", "en": "Good day, how are you?", "difficulty": 1, "vocab_ids": ["dober dan", "kako ste"]},
        {"sl": "Živjo, hvala, dobro sem.", "en": "Hello, thank you, I am well.", "difficulty": 1, "vocab_ids": ["živjo", "hvala"]},
        {"sl": "Nasvidenje, lahko noč!", "en": "Goodbye, good night!", "difficulty": 1, "vocab_ids": ["nasvidenje", "lahko noč"]},
        {"sl": "Oprostite, prosim, kje je hotel?", "en": "Excuse me, please, where is the hotel?", "difficulty": 2, "vocab_ids": ["oprostite", "prosim"]}
      ]
    }
  ]
}
```

Create all 10 units following this exact pattern. Use verified Slovenian vocabulary. The remaining 9 units are:

**Unit 2 — Števila / Numbers:** ena, dva, tri, štiri, pet, šest, sedem, osem, devet, deset, enajst, dvanajst, trinajst, štirinajst, petnajst, šestnajst, sedemnajst, osemnajst, devetnajst, dvajset

**Unit 3 — Barve / Colors:** rdeča, modra, zelena, rumena, bela, črna, oranžna, roza, vijolična, rjava, siva, zlata

**Unit 4 — Hrana / Food:** kruh, mleko, jabolko, sir, meso, riba, voda, kava, čaj, juha, solata, riž

**Unit 5 — Družina / Family:** mama, oče, brat, sestra, sin, hči, babica, dedek, teta, stric, bratranec, sestrična

**Unit 6 — Živali / Animals:** pes, mačka, ptica, riba, konj, krava, prašič, ovca, zajec, miš, medved, volk

**Unit 7 — Telo / Body:** glava, roka, noga, oko, uho, nos, usta, zob, prst, koleno, hrbet, srce

**Unit 8 — Oblačila / Clothing:** majica, hlače, čevlji, nogavice, jakna, klobuk, šal, rokavice, obleka, krilo, srajca, pas

**Unit 9 — Hiša / House:** kuhinja, soba, kopalnica, miza, stol, postelja, okno, vrata, streha, stopnice, vrt, ključ

**Unit 10 — Čas / Time:** danes, jutri, včeraj, ura, minuta, teden, mesec, leto, zjutraj, zvečer, zdaj, pozno

- [ ] **Step 4: Write the curriculum loader**

```python
# src/services/curriculum.py
import json
from pathlib import Path


class CurriculumLoader:
    def __init__(self, path: Path | None = None):
        if path is None:
            path = Path(__file__).parent.parent / "data" / "curriculum.json"
        with open(path) as f:
            self._data = json.load(f)
        self._units_by_id = {u["id"]: u for u in self._data["units"]}

    def get_units(self) -> list[dict]:
        return sorted(self._data["units"], key=lambda u: u["order"])

    def get_vocab(self, unit_id: str) -> list[dict]:
        if unit_id not in self._units_by_id:
            raise KeyError(f"Unknown unit: {unit_id}")
        return self._units_by_id[unit_id]["vocab"]

    def get_sentences(self, unit_id: str) -> list[dict]:
        if unit_id not in self._units_by_id:
            raise KeyError(f"Unknown unit: {unit_id}")
        return self._units_by_id[unit_id]["sentences"]

    def get_all_slovenian_texts(self) -> list[str]:
        texts = set()
        for unit in self._data["units"]:
            for item in unit["vocab"]:
                texts.add(item["sl"])
                texts.add(item["example"])
            for sent in unit["sentences"]:
                texts.add(sent["sl"])
        return sorted(texts)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd ~/Desktop/Slovenčk
uv run pytest tests/test_curriculum.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 6: Commit**

```bash
cd ~/Desktop/Slovenčk
git add src/data/curriculum.json src/services/curriculum.py tests/test_curriculum.py
git commit -m "feat: add curriculum data and loader for all 10 units"
```

---

### Task 3: SRS Service

**Files:**
- Create: `src/services/srs.py`
- Create: `tests/test_srs.py`

- [ ] **Step 1: Write SRS tests**

```python
# tests/test_srs.py
import pytest
from datetime import datetime, timedelta
from services.srs import SRSEngine, WordState


def test_new_word_starts_in_box_1():
    state = WordState(word="hvala")
    assert state.box == 1
    assert state.correct == 0
    assert state.incorrect == 0


def test_correct_answer_moves_up():
    engine = SRSEngine()
    state = WordState(word="hvala", box=1)
    state = engine.record_answer(state, correct=True)
    assert state.box == 2
    assert state.correct == 1


def test_incorrect_answer_resets_to_box_1():
    engine = SRSEngine()
    state = WordState(word="hvala", box=3)
    state = engine.record_answer(state, correct=False)
    assert state.box == 1
    assert state.incorrect == 1


def test_box_5_is_max():
    engine = SRSEngine()
    state = WordState(word="hvala", box=5)
    state = engine.record_answer(state, correct=True)
    assert state.box == 5


def test_is_due_box_1_always_due():
    engine = SRSEngine()
    state = WordState(word="hvala", box=1, last_reviewed=datetime.now())
    assert engine.is_due(state) is True


def test_is_due_box_2_after_1_day():
    engine = SRSEngine()
    state = WordState(word="hvala", box=2, last_reviewed=datetime.now() - timedelta(days=2))
    assert engine.is_due(state) is True


def test_is_not_due_box_2_same_day():
    engine = SRSEngine()
    state = WordState(word="hvala", box=2, last_reviewed=datetime.now())
    assert engine.is_due(state) is False


def test_is_due_box_5_after_14_days():
    engine = SRSEngine()
    state = WordState(word="hvala", box=5, last_reviewed=datetime.now() - timedelta(days=15))
    assert engine.is_due(state) is True


def test_is_learned():
    engine = SRSEngine()
    state = WordState(word="hvala", box=5)
    assert engine.is_learned(state) is True
    state2 = WordState(word="hvala", box=3)
    assert engine.is_learned(state2) is False


def test_word_state_to_dict_roundtrip():
    state = WordState(word="hvala", box=3, correct=5, incorrect=2, last_reviewed=datetime(2026, 4, 28, 12, 0, 0))
    d = state.to_dict()
    restored = WordState.from_dict(d)
    assert restored.word == state.word
    assert restored.box == state.box
    assert restored.correct == state.correct
    assert restored.incorrect == state.incorrect
    assert restored.last_reviewed == state.last_reviewed
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/Desktop/Slovenčk
uv run pytest tests/test_srs.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'services.srs'`

- [ ] **Step 3: Implement SRS engine**

```python
# src/services/srs.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta


BOX_INTERVALS = {
    1: timedelta(days=0),   # always due
    2: timedelta(days=1),
    3: timedelta(days=3),
    4: timedelta(days=7),
    5: timedelta(days=14),
}

MAX_BOX = 5


@dataclass
class WordState:
    word: str
    box: int = 1
    correct: int = 0
    incorrect: int = 0
    last_reviewed: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "box": self.box,
            "correct": self.correct,
            "incorrect": self.incorrect,
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "WordState":
        return cls(
            word=d["word"],
            box=d["box"],
            correct=d["correct"],
            incorrect=d["incorrect"],
            last_reviewed=datetime.fromisoformat(d["last_reviewed"]) if d["last_reviewed"] else None,
        )


class SRSEngine:
    def record_answer(self, state: WordState, correct: bool) -> WordState:
        if correct:
            new_box = min(state.box + 1, MAX_BOX)
            return WordState(
                word=state.word,
                box=new_box,
                correct=state.correct + 1,
                incorrect=state.incorrect,
                last_reviewed=datetime.now(),
            )
        else:
            return WordState(
                word=state.word,
                box=1,
                correct=state.correct,
                incorrect=state.incorrect + 1,
                last_reviewed=datetime.now(),
            )

    def is_due(self, state: WordState) -> bool:
        if state.box == 1:
            return True
        if state.last_reviewed is None:
            return True
        elapsed = datetime.now() - state.last_reviewed
        return elapsed >= BOX_INTERVALS[state.box]

    def is_learned(self, state: WordState) -> bool:
        return state.box >= MAX_BOX
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/Desktop/Slovenčk
uv run pytest tests/test_srs.py -v
```

Expected: all 11 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd ~/Desktop/Slovenčk
git add src/services/srs.py tests/test_srs.py
git commit -m "feat: add SRS engine with Leitner box algorithm"
```

---

### Task 4: Progress Service

**Files:**
- Create: `src/services/progress.py`
- Create: `tests/test_progress.py`

- [ ] **Step 1: Write progress service tests**

```python
# tests/test_progress.py
import pytest
import json
from pathlib import Path
from services.progress import ProgressManager


@pytest.fixture
def tmp_progress(tmp_path):
    return ProgressManager(tmp_path / "progress.json")


def test_fresh_progress_has_empty_state(tmp_progress):
    assert tmp_progress.get_lesson_status("pozdravi") == "not_started"
    assert tmp_progress.get_words_state() == {}


def test_set_lesson_status(tmp_progress):
    tmp_progress.set_lesson_status("pozdravi", "in_progress")
    assert tmp_progress.get_lesson_status("pozdravi") == "in_progress"


def test_set_lesson_score(tmp_progress):
    tmp_progress.set_lesson_score("pozdravi", 8)
    assert tmp_progress.get_lesson_score("pozdravi") == 8
    tmp_progress.set_lesson_score("pozdravi", 6)
    assert tmp_progress.get_lesson_score("pozdravi") == 8  # keeps best


def test_update_word_state(tmp_progress):
    from services.srs import WordState
    state = WordState(word="hvala", box=2, correct=3, incorrect=1)
    tmp_progress.update_word_state(state)
    loaded = tmp_progress.get_word_state("hvala")
    assert loaded.box == 2
    assert loaded.correct == 3


def test_save_and_load(tmp_progress, tmp_path):
    from services.srs import WordState
    tmp_progress.set_lesson_status("pozdravi", "completed")
    tmp_progress.set_lesson_score("pozdravi", 9)
    tmp_progress.update_word_state(WordState(word="hvala", box=3, correct=5, incorrect=1))
    tmp_progress.save()

    loaded = ProgressManager(tmp_path / "progress.json")
    assert loaded.get_lesson_status("pozdravi") == "completed"
    assert loaded.get_lesson_score("pozdravi") == 9
    assert loaded.get_word_state("hvala").box == 3


def test_stats(tmp_progress):
    from services.srs import WordState
    tmp_progress.set_lesson_status("pozdravi", "completed")
    tmp_progress.set_lesson_status("stevila", "completed")
    tmp_progress.update_word_state(WordState(word="hvala", box=5))
    tmp_progress.update_word_state(WordState(word="da", box=3))
    stats = tmp_progress.get_stats()
    assert stats["lessons_completed"] == 2
    assert stats["words_learned"] == 1
    assert stats["words_in_progress"] == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/Desktop/Slovenčk
uv run pytest tests/test_progress.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement progress service**

```python
# src/services/progress.py
import json
from pathlib import Path
from services.srs import WordState, MAX_BOX


class ProgressManager:
    def __init__(self, path: Path | None = None):
        if path is None:
            path = Path(__file__).parent.parent / "data" / "progress.json"
        self._path = path
        self._lessons: dict[str, dict] = {}
        self._words: dict[str, WordState] = {}
        if self._path.exists():
            self._load()

    def _load(self):
        with open(self._path) as f:
            data = json.load(f)
        self._lessons = data.get("lessons", {})
        for word_data in data.get("words", []):
            state = WordState.from_dict(word_data)
            self._words[state.word] = state

    def save(self):
        data = {
            "lessons": self._lessons,
            "words": [s.to_dict() for s in self._words.values()],
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(data, f, indent=2)

    def get_lesson_status(self, unit_id: str) -> str:
        return self._lessons.get(unit_id, {}).get("status", "not_started")

    def set_lesson_status(self, unit_id: str, status: str):
        if unit_id not in self._lessons:
            self._lessons[unit_id] = {}
        self._lessons[unit_id]["status"] = status
        self.save()

    def get_lesson_score(self, unit_id: str) -> int:
        return self._lessons.get(unit_id, {}).get("best_score", 0)

    def set_lesson_score(self, unit_id: str, score: int):
        if unit_id not in self._lessons:
            self._lessons[unit_id] = {}
        current_best = self._lessons[unit_id].get("best_score", 0)
        self._lessons[unit_id]["best_score"] = max(current_best, score)
        self.save()

    def get_words_state(self) -> dict[str, WordState]:
        return dict(self._words)

    def get_word_state(self, word: str) -> WordState | None:
        return self._words.get(word)

    def update_word_state(self, state: WordState):
        self._words[state.word] = state
        self.save()

    def get_stats(self) -> dict:
        lessons_completed = sum(
            1 for l in self._lessons.values() if l.get("status") == "completed"
        )
        words_learned = sum(1 for w in self._words.values() if w.box >= MAX_BOX)
        words_in_progress = sum(1 for w in self._words.values() if 1 < w.box < MAX_BOX)
        return {
            "lessons_completed": lessons_completed,
            "words_learned": words_learned,
            "words_in_progress": words_in_progress,
        }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/Desktop/Slovenčk
uv run pytest tests/test_progress.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd ~/Desktop/Slovenčk
git add src/services/progress.py tests/test_progress.py
git commit -m "feat: add progress manager with save/load and stats"
```

---

### Task 5: Exercise Types (Pure Logic)

**Files:**
- Create: `src/exercises/base.py`
- Create: `src/exercises/flashcard.py`
- Create: `src/exercises/multiple_choice.py`
- Create: `src/exercises/sentence_building.py`
- Create: `src/exercises/fill_blank.py`
- Create: `src/exercises/listening.py`
- Create: `src/exercises/typing_ex.py`
- Create: `tests/test_exercises.py`

- [ ] **Step 1: Write exercise tests**

```python
# tests/test_exercises.py
import pytest
from exercises.base import ExerciseType
from exercises.flashcard import FlashcardExercise
from exercises.multiple_choice import MultipleChoiceExercise
from exercises.sentence_building import SentenceBuildingExercise
from exercises.fill_blank import FillBlankExercise
from exercises.listening import ListeningExercise
from exercises.typing_ex import TypingExercise


class TestFlashcard:
    def test_create(self):
        ex = FlashcardExercise(word_sl="hvala", word_en="thank you", audio_file="abc.mp3")
        assert ex.exercise_type == ExerciseType.FLASHCARD
        assert ex.word_sl == "hvala"
        assert ex.word_en == "thank you"

    def test_check_always_correct(self):
        ex = FlashcardExercise(word_sl="hvala", word_en="thank you", audio_file="abc.mp3")
        assert ex.check_answer("") is True  # flashcard is self-assessed


class TestMultipleChoice:
    def test_create(self):
        ex = MultipleChoiceExercise(
            prompt="What is 'hvala' in English?",
            choices=["hello", "thank you", "goodbye", "please"],
            correct_index=1,
            word_sl="hvala",
        )
        assert ex.exercise_type == ExerciseType.MULTIPLE_CHOICE

    def test_correct_answer(self):
        ex = MultipleChoiceExercise(
            prompt="What is 'hvala' in English?",
            choices=["hello", "thank you", "goodbye", "please"],
            correct_index=1,
            word_sl="hvala",
        )
        assert ex.check_answer(1) is True

    def test_wrong_answer(self):
        ex = MultipleChoiceExercise(
            prompt="What is 'hvala' in English?",
            choices=["hello", "thank you", "goodbye", "please"],
            correct_index=1,
            word_sl="hvala",
        )
        assert ex.check_answer(0) is False


class TestSentenceBuilding:
    def test_correct_order(self):
        ex = SentenceBuildingExercise(
            prompt="Build: 'Good day, how are you?'",
            correct_words=["Dober", "dan,", "kako", "ste?"],
            scrambled_words=["kako", "dan,", "Dober", "ste?"],
            word_sl="dober dan",
        )
        assert ex.check_answer(["Dober", "dan,", "kako", "ste?"]) is True

    def test_wrong_order(self):
        ex = SentenceBuildingExercise(
            prompt="Build: 'Good day, how are you?'",
            correct_words=["Dober", "dan,", "kako", "ste?"],
            scrambled_words=["kako", "dan,", "Dober", "ste?"],
            word_sl="dober dan",
        )
        assert ex.check_answer(["kako", "dan,", "Dober", "ste?"]) is False


class TestFillBlank:
    def test_correct(self):
        ex = FillBlankExercise(
            sentence_with_blank="_____, kako ste?",
            correct_answer="Dober dan",
            word_bank=["Dober dan", "Živjo", "Hvala", "Nasvidenje"],
            word_sl="dober dan",
        )
        assert ex.check_answer("Dober dan") is True

    def test_wrong(self):
        ex = FillBlankExercise(
            sentence_with_blank="_____, kako ste?",
            correct_answer="Dober dan",
            word_bank=["Dober dan", "Živjo", "Hvala", "Nasvidenje"],
            word_sl="dober dan",
        )
        assert ex.check_answer("Živjo") is False


class TestListening:
    def test_correct(self):
        ex = ListeningExercise(
            audio_file="hvala.mp3",
            choices=["hvala", "prosim", "živjo", "da"],
            correct_index=0,
            word_sl="hvala",
        )
        assert ex.check_answer(0) is True

    def test_wrong(self):
        ex = ListeningExercise(
            audio_file="hvala.mp3",
            choices=["hvala", "prosim", "živjo", "da"],
            correct_index=0,
            word_sl="hvala",
        )
        assert ex.check_answer(2) is False


class TestTyping:
    def test_correct_exact(self):
        ex = TypingExercise(
            prompt="Type the English for: hvala",
            correct_answer="thank you",
            word_sl="hvala",
        )
        assert ex.check_answer("thank you") is True

    def test_correct_case_insensitive(self):
        ex = TypingExercise(
            prompt="Type the English for: hvala",
            correct_answer="thank you",
            word_sl="hvala",
        )
        assert ex.check_answer("Thank You") is True

    def test_wrong(self):
        ex = TypingExercise(
            prompt="Type the English for: hvala",
            correct_answer="thank you",
            word_sl="hvala",
        )
        assert ex.check_answer("hello") is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/Desktop/Slovenčk
uv run pytest tests/test_exercises.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement base exercise**

```python
# src/exercises/base.py
from enum import Enum
from dataclasses import dataclass


class ExerciseType(Enum):
    FLASHCARD = "flashcard"
    MULTIPLE_CHOICE = "multiple_choice"
    SENTENCE_BUILDING = "sentence_building"
    FILL_BLANK = "fill_blank"
    LISTENING = "listening"
    TYPING = "typing"
```

- [ ] **Step 4: Implement all 6 exercise types**

```python
# src/exercises/flashcard.py
from dataclasses import dataclass
from exercises.base import ExerciseType


@dataclass
class FlashcardExercise:
    word_sl: str
    word_en: str
    audio_file: str
    exercise_type: ExerciseType = ExerciseType.FLASHCARD

    def check_answer(self, answer) -> bool:
        return True  # self-assessed
```

```python
# src/exercises/multiple_choice.py
from dataclasses import dataclass
from exercises.base import ExerciseType


@dataclass
class MultipleChoiceExercise:
    prompt: str
    choices: list[str]
    correct_index: int
    word_sl: str
    exercise_type: ExerciseType = ExerciseType.MULTIPLE_CHOICE

    def check_answer(self, selected_index: int) -> bool:
        return selected_index == self.correct_index

    @property
    def correct_answer(self) -> str:
        return self.choices[self.correct_index]
```

```python
# src/exercises/sentence_building.py
from dataclasses import dataclass
from exercises.base import ExerciseType


@dataclass
class SentenceBuildingExercise:
    prompt: str
    correct_words: list[str]
    scrambled_words: list[str]
    word_sl: str
    exercise_type: ExerciseType = ExerciseType.SENTENCE_BUILDING

    def check_answer(self, ordered_words: list[str]) -> bool:
        return ordered_words == self.correct_words

    @property
    def correct_answer(self) -> str:
        return " ".join(self.correct_words)
```

```python
# src/exercises/fill_blank.py
from dataclasses import dataclass
from exercises.base import ExerciseType


@dataclass
class FillBlankExercise:
    sentence_with_blank: str
    correct_answer: str
    word_bank: list[str]
    word_sl: str
    exercise_type: ExerciseType = ExerciseType.FILL_BLANK

    def check_answer(self, answer: str) -> bool:
        return answer.strip().lower() == self.correct_answer.strip().lower()
```

```python
# src/exercises/listening.py
from dataclasses import dataclass
from exercises.base import ExerciseType


@dataclass
class ListeningExercise:
    audio_file: str
    choices: list[str]
    correct_index: int
    word_sl: str
    exercise_type: ExerciseType = ExerciseType.LISTENING

    def check_answer(self, selected_index: int) -> bool:
        return selected_index == self.correct_index

    @property
    def correct_answer(self) -> str:
        return self.choices[self.correct_index]
```

```python
# src/exercises/typing_ex.py
from dataclasses import dataclass
from exercises.base import ExerciseType


@dataclass
class TypingExercise:
    prompt: str
    correct_answer: str
    word_sl: str
    exercise_type: ExerciseType = ExerciseType.TYPING

    def check_answer(self, answer: str) -> bool:
        return answer.strip().lower() == self.correct_answer.strip().lower()
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd ~/Desktop/Slovenčk
uv run pytest tests/test_exercises.py -v
```

Expected: all 13 tests PASS.

- [ ] **Step 6: Commit**

```bash
cd ~/Desktop/Slovenčk
git add src/exercises/ tests/test_exercises.py
git commit -m "feat: add 6 exercise types with answer checking logic"
```

---

### Task 6: Session Builder

**Files:**
- Create: `src/exercises/session.py`
- Create: `tests/test_session.py`

- [ ] **Step 1: Write session builder tests**

```python
# tests/test_session.py
import pytest
from datetime import datetime, timedelta
from exercises.session import SessionBuilder
from exercises.base import ExerciseType
from services.curriculum import CurriculumLoader
from services.srs import WordState
from services.progress import ProgressManager


@pytest.fixture
def loader():
    return CurriculumLoader()


@pytest.fixture
def progress(tmp_path):
    return ProgressManager(tmp_path / "progress.json")


@pytest.fixture
def builder(loader, progress):
    return SessionBuilder(loader, progress)


def test_build_session_returns_10_exercises(builder):
    exercises = builder.build("pozdravi")
    assert len(exercises) == 10


def test_session_has_mixed_types(builder):
    exercises = builder.build("pozdravi")
    types = {ex.exercise_type for ex in exercises}
    assert len(types) >= 3  # at least 3 different exercise types


def test_no_two_same_types_in_a_row(builder):
    exercises = builder.build("pozdravi")
    for i in range(1, len(exercises)):
        assert exercises[i].exercise_type != exercises[i - 1].exercise_type


def test_due_words_prioritized(builder, progress):
    # Mark a word as due (box 1)
    state = WordState(word="hvala", box=1, last_reviewed=datetime.now() - timedelta(days=1))
    progress.update_word_state(state)
    exercises = builder.build("pozdravi")
    exercise_words = [ex.word_sl for ex in exercises]
    assert "hvala" in exercise_words


def test_builds_for_any_unit(builder):
    exercises = builder.build("stevila")
    assert len(exercises) == 10
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/Desktop/Slovenčk
uv run pytest tests/test_session.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement session builder**

```python
# src/exercises/session.py
import random
import hashlib
from exercises.base import ExerciseType
from exercises.flashcard import FlashcardExercise
from exercises.multiple_choice import MultipleChoiceExercise
from exercises.sentence_building import SentenceBuildingExercise
from exercises.fill_blank import FillBlankExercise
from exercises.listening import ListeningExercise
from exercises.typing_ex import TypingExercise
from services.curriculum import CurriculumLoader
from services.progress import ProgressManager
from services.srs import SRSEngine, WordState

SESSION_SIZE = 10


def _audio_path(text: str) -> str:
    h = hashlib.md5(text.encode()).hexdigest()
    return f"{h}.mp3"


class SessionBuilder:
    def __init__(self, curriculum: CurriculumLoader, progress: ProgressManager):
        self._curriculum = curriculum
        self._progress = progress
        self._srs = SRSEngine()

    def build(self, unit_id: str) -> list:
        vocab = self._curriculum.get_vocab(unit_id)
        sentences = self._curriculum.get_sentences(unit_id)
        words_state = self._progress.get_words_state()

        # Separate due words and new words
        due_words = []
        new_words = []
        for item in vocab:
            state = words_state.get(item["sl"])
            if state and self._srs.is_due(state):
                due_words.append(item)
            elif state is None:
                new_words.append(item)

        # Pick words for this session: due first, then new
        selected = due_words[:SESSION_SIZE]
        remaining = SESSION_SIZE - len(selected)
        if remaining > 0:
            random.shuffle(new_words)
            selected.extend(new_words[:remaining])

        # If still not enough, add non-due reviewed words
        if len(selected) < SESSION_SIZE:
            reviewed = [v for v in vocab if v not in selected]
            random.shuffle(reviewed)
            selected.extend(reviewed[: SESSION_SIZE - len(selected)])

        selected = selected[:SESSION_SIZE]

        # Build exercises with mixed types, no two same in a row
        all_vocab_words = [v["en"] for v in vocab]
        exercise_types = [
            ExerciseType.FLASHCARD,
            ExerciseType.MULTIPLE_CHOICE,
            ExerciseType.SENTENCE_BUILDING,
            ExerciseType.FILL_BLANK,
            ExerciseType.LISTENING,
            ExerciseType.TYPING,
        ]

        exercises = []
        last_type = None
        for item in selected:
            available = [t for t in exercise_types if t != last_type]

            # Sentence building needs a sentence — only use if we have one
            item_sentences = [s for s in sentences if item["sl"] in s.get("vocab_ids", [])]
            if not item_sentences:
                available = [t for t in available if t != ExerciseType.SENTENCE_BUILDING]

            chosen_type = random.choice(available)
            ex = self._create_exercise(chosen_type, item, all_vocab_words, item_sentences)
            exercises.append(ex)
            last_type = chosen_type

        return exercises

    def _create_exercise(self, ex_type: ExerciseType, item: dict, all_en_words: list[str], sentences: list[dict]):
        word_sl = item["sl"]
        word_en = item["en"]
        audio = _audio_path(word_sl)

        if ex_type == ExerciseType.FLASHCARD:
            return FlashcardExercise(word_sl=word_sl, word_en=word_en, audio_file=audio)

        elif ex_type == ExerciseType.MULTIPLE_CHOICE:
            distractors = [w for w in all_en_words if w != word_en]
            random.shuffle(distractors)
            choices = distractors[:3] + [word_en]
            random.shuffle(choices)
            return MultipleChoiceExercise(
                prompt=f"What is '{word_sl}' in English?",
                choices=choices,
                correct_index=choices.index(word_en),
                word_sl=word_sl,
            )

        elif ex_type == ExerciseType.SENTENCE_BUILDING:
            sent = random.choice(sentences)
            words = sent["sl"].split()
            scrambled = words[:]
            while scrambled == words and len(words) > 1:
                random.shuffle(scrambled)
            return SentenceBuildingExercise(
                prompt=f"Build: '{sent['en']}'",
                correct_words=words,
                scrambled_words=scrambled,
                word_sl=word_sl,
            )

        elif ex_type == ExerciseType.FILL_BLANK:
            sentence = item["example"]
            sentence_en = item["example_en"]
            blank_sentence = sentence.replace(word_sl, "_____", 1)
            if blank_sentence == sentence:
                # word not found verbatim in sentence, use a simpler blank
                blank_sentence = f"_____ = {word_en}"
            distractors = [v for v in [i["sl"] for i in self._curriculum.get_vocab(
                self._curriculum.get_units()[0]["id"])] if v != word_sl][:3]
            word_bank = distractors + [word_sl]
            random.shuffle(word_bank)
            return FillBlankExercise(
                sentence_with_blank=blank_sentence,
                correct_answer=word_sl,
                word_bank=word_bank,
                word_sl=word_sl,
            )

        elif ex_type == ExerciseType.LISTENING:
            all_sl = [item["sl"]] + [w for w in [v["sl"] for v in self._curriculum.get_vocab(
                self._curriculum.get_units()[0]["id"])] if w != word_sl][:3]
            random.shuffle(all_sl)
            return ListeningExercise(
                audio_file=audio,
                choices=all_sl,
                correct_index=all_sl.index(word_sl),
                word_sl=word_sl,
            )

        elif ex_type == ExerciseType.TYPING:
            return TypingExercise(
                prompt=f"Type the English for: {word_sl}",
                correct_answer=word_en,
                word_sl=word_sl,
            )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/Desktop/Slovenčk
uv run pytest tests/test_session.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd ~/Desktop/Slovenčk
git add src/exercises/session.py tests/test_session.py
git commit -m "feat: add session builder with SRS-prioritized exercise selection"
```

---

### Task 7: Audio Generation Script

**Files:**
- Create: `scripts/generate_audio.py`

- [ ] **Step 1: Write the audio generation script**

```python
# scripts/generate_audio.py
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
```

- [ ] **Step 2: Test the script runs (generates a few files)**

```bash
cd ~/Desktop/Slovenčk
uv run python scripts/generate_audio.py
```

Expected: prints progress, creates .mp3 files in `src/audio/`.

- [ ] **Step 3: Verify audio files exist**

```bash
ls ~/Desktop/Slovenčk/src/audio/ | head -10
ls ~/Desktop/Slovenčk/src/audio/ | wc -l
```

Expected: multiple .mp3 files exist.

- [ ] **Step 4: Commit (script only, not audio files — add audio to .gitignore)**

Create/update `.gitignore`:
```
src/audio/*.mp3
src/data/progress.json
__pycache__/
*.pyc
.venv/
```

```bash
cd ~/Desktop/Slovenčk
git add scripts/generate_audio.py .gitignore
git commit -m "feat: add TTS audio generation script"
```

---

### Task 8: Gemini Asset & Theme Generation Script

**Files:**
- Create: `scripts/generate_assets.py`
- Create: `src/services/gemini.py`

- [ ] **Step 1: Write the Gemini service**

```python
# src/services/gemini.py
import os
from google import genai
from google.genai import types


def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY environment variable")
    return genai.Client(api_key=api_key)


def generate_image(client: genai.Client, prompt: str) -> bytes:
    """Generate an image using Gemini's image generation and return PNG bytes."""
    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        config=types.GenerateImagesConfig(number_of_images=1),
    )
    return response.generated_images[0].image.image_bytes


def generate_text(client: genai.Client, prompt: str) -> str:
    """Generate text using Gemini and return the response."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text
```

- [ ] **Step 2: Write the asset generation script**

```python
# scripts/generate_assets.py
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
        icon_bytes = generate_image(client, prompt)
        icon_path.write_bytes(icon_bytes)
        print(f"  Saved: {icon_path}")

    # Generate Kivy theme
    theme_path = THEME_DIR / "style.kv"
    if not theme_path.exists():
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
```

- [ ] **Step 3: Add assets to .gitignore (generated, large binaries)**

Append to `.gitignore`:
```
src/assets/*.png
```

- [ ] **Step 4: Commit**

```bash
cd ~/Desktop/Slovenčk
git add src/services/gemini.py scripts/generate_assets.py .gitignore
git commit -m "feat: add Gemini asset and theme generation script"
```

---

### Task 9: Kivy App Shell & Navigation

**Files:**
- Create: `src/main.py`
- Create: `src/services/audio.py`
- Create: `src/theme/style.kv` (placeholder if not generated)

- [ ] **Step 1: Create audio playback helper**

```python
# src/services/audio.py
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
```

- [ ] **Step 2: Create a placeholder theme file (used if Gemini hasn't been run)**

```kv
# src/theme/style.kv
# Default theme — regenerate with: uv run python scripts/generate_assets.py

<RoundedButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    canvas.before:
        Color:
            rgba: (0.345, 0.8, 0.008, 1) if self.state == 'normal' else (0.275, 0.64, 0.006, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15]
    color: 1, 1, 1, 1
    font_size: '18sp'
    size_hint_y: None
    height: '50dp'

<CardBox@BoxLayout>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10]
    padding: '15dp'
    spacing: '10dp'

<AppLabel@Label>:
    font_size: '20sp'
    color: 0.2, 0.2, 0.2, 1

<TitleLabel@Label>:
    font_size: '28sp'
    color: 0.2, 0.2, 0.2, 1
    bold: True

<AppProgressBar@ProgressBar>:
    max: 100
    size_hint_y: None
    height: '8dp'

<AppTextInput@TextInput>:
    font_size: '20sp'
    multiline: False
    size_hint_y: None
    height: '50dp'
    padding: [15, 12, 15, 12]
```

- [ ] **Step 3: Create main.py with ScreenManager**

```python
# src/main.py
import os
import sys
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).parent))

# Set window size before Kivy init (desktop testing)
os.environ.setdefault("KIVY_WINDOW", "sdl2")
from kivy.config import Config
Config.set("graphics", "width", "360")
Config.set("graphics", "height", "640")
Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from screens.home import HomeScreen
from screens.lesson_select import LessonSelectScreen
from screens.exercise import ExerciseScreen
from screens.results import ResultsScreen
from services.curriculum import CurriculumLoader
from services.progress import ProgressManager

# Load theme
theme_path = Path(__file__).parent / "theme" / "style.kv"
if theme_path.exists():
    Builder.load_file(str(theme_path))


class SlovencekApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.curriculum = CurriculumLoader()
        self.progress = ProgressManager()

    def build(self):
        self.title = "Slovenčk"
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(LessonSelectScreen(name="lesson_select"))
        sm.add_widget(ExerciseScreen(name="exercise"))
        sm.add_widget(ResultsScreen(name="results"))
        return sm


if __name__ == "__main__":
    SlovencekApp().run()
```

- [ ] **Step 4: Commit**

```bash
cd ~/Desktop/Slovenčk
git add src/main.py src/services/audio.py src/theme/style.kv
git commit -m "feat: add Kivy app shell with screen manager and theme"
```

---

### Task 10: Home Screen

**Files:**
- Create: `src/screens/home.py`

- [ ] **Step 1: Implement home screen**

```python
# src/screens/home.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
from kivy.metrics import dp


class HomeScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        stats = app.progress.get_stats()

        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))

        # Title
        title = Label(
            text="Slovenčk",
            font_size="36sp",
            bold=True,
            color=(0.345, 0.8, 0.008, 1),
            size_hint_y=None,
            height=dp(60),
        )
        root.add_widget(title)

        # Subtitle
        subtitle = Label(
            text="Learn Slovenian",
            font_size="18sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(30),
        )
        root.add_widget(subtitle)

        # Stats
        stats_text = (
            f"Lessons completed: {stats['lessons_completed']}\n"
            f"Words learned: {stats['words_learned']}\n"
            f"Words in progress: {stats['words_in_progress']}"
        )
        stats_label = Label(
            text=stats_text,
            font_size="18sp",
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(100),
            halign="center",
        )
        stats_label.bind(size=stats_label.setter("text_size"))
        root.add_widget(stats_label)

        # Spacer
        root.add_widget(BoxLayout())

        # Continue button
        continue_btn = Button(
            text="Continue Learning",
            font_size="20sp",
            size_hint_y=None,
            height=dp(55),
            background_color=(0.345, 0.8, 0.008, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        continue_btn.bind(on_release=self._on_continue)
        root.add_widget(continue_btn)

        # Lesson select button
        select_btn = Button(
            text="All Lessons",
            font_size="18sp",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        select_btn.bind(on_release=self._on_select)
        root.add_widget(select_btn)

        # Bottom spacer
        root.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))

        self.add_widget(root)

    def _on_continue(self, *args):
        app = App.get_running_app()
        units = app.curriculum.get_units()
        # Find first incomplete lesson
        for unit in units:
            status = app.progress.get_lesson_status(unit["id"])
            if status != "completed":
                self.manager.get_screen("exercise").unit_id = unit["id"]
                self.manager.current = "exercise"
                return
        # All done — go to lesson select
        self.manager.current = "lesson_select"

    def _on_select(self, *args):
        self.manager.current = "lesson_select"
```

- [ ] **Step 2: Test locally — app launches and shows home screen**

```bash
cd ~/Desktop/Slovenčk
uv run python src/main.py
```

Expected: Kivy window opens (360x640), shows "Slovenčk" title, stats, and two buttons. Close the window.

- [ ] **Step 3: Commit**

```bash
cd ~/Desktop/Slovenčk
git add src/screens/home.py
git commit -m "feat: add home screen with progress stats and navigation"
```

---

### Task 11: Lesson Select Screen

**Files:**
- Create: `src/screens/lesson_select.py`

- [ ] **Step 1: Implement lesson select screen**

```python
# src/screens/lesson_select.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle


class LessonCard(BoxLayout):
    def __init__(self, unit, status, score, locked, on_tap, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(80)
        self.padding = dp(15)
        self.spacing = dp(10)

        # Background
        with self.canvas.before:
            if locked:
                Color(0.85, 0.85, 0.85, 1)
            elif status == "completed":
                Color(0.9, 1, 0.9, 1)
            else:
                Color(1, 1, 1, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Text info
        text_box = BoxLayout(orientation="vertical", spacing=dp(2))
        name_label = Label(
            text=f"{unit['name_sl']} / {unit['name_en']}",
            font_size="18sp",
            color=(0.5, 0.5, 0.5, 1) if locked else (0.2, 0.2, 0.2, 1),
            halign="left",
            valign="center",
            size_hint_x=1,
        )
        name_label.bind(size=name_label.setter("text_size"))
        text_box.add_widget(name_label)

        status_text = "Locked" if locked else status.replace("_", " ").title()
        if score > 0:
            status_text += f" (Best: {score}/10)"
        status_label = Label(
            text=status_text,
            font_size="14sp",
            color=(0.6, 0.6, 0.6, 1),
            halign="left",
            valign="center",
        )
        status_label.bind(size=status_label.setter("text_size"))
        text_box.add_widget(status_label)

        self.add_widget(text_box)

        if not locked:
            # Make it tappable
            btn = Button(
                text="Start" if status == "not_started" else "Continue" if status == "in_progress" else "Review",
                font_size="14sp",
                size_hint=(None, None),
                width=dp(70),
                height=dp(40),
                pos_hint={"center_y": 0.5},
                background_color=(0.345, 0.8, 0.008, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(on_release=lambda *a: on_tap(unit["id"]))
            self.add_widget(btn)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size


class LessonSelectScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        units = app.curriculum.get_units()

        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(
            text="<",
            size_hint=(None, None),
            width=dp(40),
            height=dp(40),
            font_size="20sp",
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0.2, 0.2, 0.2, 1),
        )
        back_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "home"))
        header.add_widget(back_btn)
        header.add_widget(Label(
            text="Lessons",
            font_size="24sp",
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
        ))
        root.add_widget(header)

        # Scrollable lesson list
        scroll = ScrollView()
        lesson_list = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        lesson_list.bind(minimum_height=lesson_list.setter("height"))

        prev_completed = True  # first lesson is always unlocked
        for unit in units:
            status = app.progress.get_lesson_status(unit["id"])
            score = app.progress.get_lesson_score(unit["id"])
            locked = not prev_completed
            card = LessonCard(
                unit=unit,
                status=status,
                score=score,
                locked=locked,
                on_tap=self._start_lesson,
            )
            lesson_list.add_widget(card)
            if status == "completed":
                prev_completed = True
            else:
                prev_completed = False

        scroll.add_widget(lesson_list)
        root.add_widget(scroll)
        self.add_widget(root)

    def _start_lesson(self, unit_id):
        self.manager.get_screen("exercise").unit_id = unit_id
        self.manager.current = "exercise"
```

- [ ] **Step 2: Test locally — navigate to lesson select**

```bash
cd ~/Desktop/Slovenčk
uv run python src/main.py
```

Expected: Click "All Lessons" on home screen → see scrollable list of 10 lesson units. First is unlocked, rest are locked. Close the window.

- [ ] **Step 3: Commit**

```bash
cd ~/Desktop/Slovenčk
git add src/screens/lesson_select.py
git commit -m "feat: add lesson select screen with lock progression"
```

---

### Task 12: Exercise Screen

**Files:**
- Create: `src/screens/exercise.py`

- [ ] **Step 1: Implement exercise screen (renders all 6 exercise types)**

```python
# src/screens/exercise.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle

from exercises.base import ExerciseType
from exercises.session import SessionBuilder
from services.srs import SRSEngine, WordState
from services.audio import play_audio


class ExerciseScreen(Screen):
    unit_id = ""

    def on_enter(self):
        app = App.get_running_app()
        builder = SessionBuilder(app.curriculum, app.progress)
        self._exercises = builder.build(self.unit_id)
        self._current_idx = 0
        self._score = 0
        self._srs = SRSEngine()
        self._show_current()

    def _show_current(self):
        self.clear_widgets()
        if self._current_idx >= len(self._exercises):
            self._finish_lesson()
            return

        ex = self._exercises[self._current_idx]
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))

        # Progress bar
        progress = ProgressBar(
            max=len(self._exercises),
            value=self._current_idx,
            size_hint_y=None,
            height=dp(8),
        )
        root.add_widget(progress)

        # Counter
        counter = Label(
            text=f"{self._current_idx + 1} / {len(self._exercises)}",
            font_size="14sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(25),
        )
        root.add_widget(counter)

        # Render by type
        if ex.exercise_type == ExerciseType.FLASHCARD:
            self._render_flashcard(root, ex)
        elif ex.exercise_type == ExerciseType.MULTIPLE_CHOICE:
            self._render_multiple_choice(root, ex)
        elif ex.exercise_type == ExerciseType.SENTENCE_BUILDING:
            self._render_sentence_building(root, ex)
        elif ex.exercise_type == ExerciseType.FILL_BLANK:
            self._render_fill_blank(root, ex)
        elif ex.exercise_type == ExerciseType.LISTENING:
            self._render_listening(root, ex)
        elif ex.exercise_type == ExerciseType.TYPING:
            self._render_typing(root, ex)

        self.add_widget(root)

    def _render_flashcard(self, root, ex):
        root.add_widget(Label(
            text="Flashcard",
            font_size="16sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(25),
        ))

        # Card area
        card_box = BoxLayout(orientation="vertical", spacing=dp(10))

        word_label = Label(
            text=ex.word_sl,
            font_size="32sp",
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
        )
        card_box.add_widget(word_label)

        self._flash_answer = Label(
            text="Tap to reveal",
            font_size="24sp",
            color=(0.6, 0.6, 0.6, 1),
        )
        card_box.add_widget(self._flash_answer)

        root.add_widget(card_box)

        # Audio button
        audio_btn = Button(
            text="Play Audio",
            size_hint_y=None,
            height=dp(45),
            font_size="16sp",
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        audio_btn.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(audio_btn)

        # Reveal button
        reveal_btn = Button(
            text="Reveal Translation",
            size_hint_y=None,
            height=dp(50),
            font_size="18sp",
            background_color=(0.345, 0.8, 0.008, 1),
            color=(1, 1, 1, 1),
        )

        def reveal(*args):
            self._flash_answer.text = ex.word_en
            self._flash_answer.color = (0.2, 0.2, 0.2, 1)
            reveal_btn.text = "I knew it!"
            reveal_btn.unbind(on_release=reveal)
            reveal_btn.bind(on_release=lambda *a: self._record_and_next(ex, True))
            # Add "I didn't know" button
            didnt_btn = Button(
                text="I didn't know",
                size_hint_y=None,
                height=dp(50),
                font_size="18sp",
                background_color=(1, 0.294, 0.294, 1),
                color=(1, 1, 1, 1),
            )
            didnt_btn.bind(on_release=lambda *a: self._record_and_next(ex, False))
            root.add_widget(didnt_btn)

        reveal_btn.bind(on_release=reveal)
        root.add_widget(reveal_btn)

    def _render_multiple_choice(self, root, ex):
        root.add_widget(Label(
            text=ex.prompt,
            font_size="22sp",
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(80),
            halign="center",
            valign="center",
        ))

        # Audio
        audio_btn = Button(
            text="Play Audio",
            size_hint_y=None,
            height=dp(40),
            font_size="14sp",
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        audio_btn.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(audio_btn)

        root.add_widget(BoxLayout(size_hint_y=0.1))  # spacer

        for i, choice in enumerate(ex.choices):
            btn = Button(
                text=choice,
                font_size="18sp",
                size_hint_y=None,
                height=dp(50),
                background_color=(0.95, 0.95, 0.95, 1),
                color=(0.2, 0.2, 0.2, 1),
            )
            btn.bind(on_release=lambda inst, idx=i: self._check_mc(ex, idx, root))
            root.add_widget(btn)

    def _check_mc(self, ex, selected, root):
        correct = ex.check_answer(selected)
        self._show_feedback(root, correct, ex.correct_answer, ex)

    def _render_sentence_building(self, root, ex):
        root.add_widget(Label(
            text=ex.prompt,
            font_size="20sp",
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(60),
            halign="center",
        ))

        # Answer area
        self._sb_selected = []
        self._sb_answer_label = Label(
            text="...",
            font_size="20sp",
            color=(0.345, 0.8, 0.008, 1),
            size_hint_y=None,
            height=dp(50),
        )
        root.add_widget(self._sb_answer_label)

        root.add_widget(BoxLayout(size_hint_y=0.1))

        # Word tiles
        self._sb_tiles_box = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(150))
        self._sb_buttons = []
        for word in ex.scrambled_words:
            btn = Button(
                text=word,
                font_size="16sp",
                size_hint_y=None,
                height=dp(45),
                background_color=(0.11, 0.69, 0.965, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(on_release=lambda inst, w=word: self._sb_tap(inst, w, ex, root))
            self._sb_buttons.append(btn)
            self._sb_tiles_box.add_widget(btn)
        root.add_widget(self._sb_tiles_box)

        # Clear button
        clear_btn = Button(
            text="Clear",
            size_hint_y=None,
            height=dp(40),
            font_size="14sp",
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0.2, 0.2, 0.2, 1),
        )
        clear_btn.bind(on_release=lambda *a: self._sb_clear())
        root.add_widget(clear_btn)

    def _sb_tap(self, btn_inst, word, ex, root):
        self._sb_selected.append(word)
        btn_inst.disabled = True
        self._sb_answer_label.text = " ".join(self._sb_selected)
        if len(self._sb_selected) == len(ex.correct_words):
            correct = ex.check_answer(self._sb_selected)
            self._show_feedback(root, correct, ex.correct_answer, ex)

    def _sb_clear(self):
        self._sb_selected.clear()
        self._sb_answer_label.text = "..."
        for btn in self._sb_buttons:
            btn.disabled = False

    def _render_fill_blank(self, root, ex):
        root.add_widget(Label(
            text="Fill in the blank:",
            font_size="16sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(25),
        ))
        root.add_widget(Label(
            text=ex.sentence_with_blank,
            font_size="20sp",
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(60),
            halign="center",
        ))

        root.add_widget(BoxLayout(size_hint_y=0.1))

        for word in ex.word_bank:
            btn = Button(
                text=word,
                font_size="18sp",
                size_hint_y=None,
                height=dp(50),
                background_color=(0.95, 0.95, 0.95, 1),
                color=(0.2, 0.2, 0.2, 1),
            )
            btn.bind(on_release=lambda inst, w=word: self._check_fill(ex, w, root))
            root.add_widget(btn)

    def _check_fill(self, ex, answer, root):
        correct = ex.check_answer(answer)
        self._show_feedback(root, correct, ex.correct_answer, ex)

    def _render_listening(self, root, ex):
        root.add_widget(Label(
            text="What do you hear?",
            font_size="22sp",
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(50),
        ))

        # Play audio button (big)
        audio_btn = Button(
            text="Play Audio",
            font_size="20sp",
            size_hint_y=None,
            height=dp(60),
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        audio_btn.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(audio_btn)

        # Auto-play on enter
        Clock.schedule_once(lambda dt: play_audio(ex.word_sl), 0.5)

        root.add_widget(BoxLayout(size_hint_y=0.1))

        for i, choice in enumerate(ex.choices):
            btn = Button(
                text=choice,
                font_size="18sp",
                size_hint_y=None,
                height=dp(50),
                background_color=(0.95, 0.95, 0.95, 1),
                color=(0.2, 0.2, 0.2, 1),
            )
            btn.bind(on_release=lambda inst, idx=i: self._check_listening(ex, idx, root))
            root.add_widget(btn)

    def _check_listening(self, ex, selected, root):
        correct = ex.check_answer(selected)
        self._show_feedback(root, correct, ex.correct_answer, ex)

    def _render_typing(self, root, ex):
        root.add_widget(Label(
            text=ex.prompt,
            font_size="22sp",
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(60),
            halign="center",
        ))

        # Audio
        audio_btn = Button(
            text="Play Audio",
            size_hint_y=None,
            height=dp(40),
            font_size="14sp",
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        audio_btn.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(audio_btn)

        root.add_widget(BoxLayout(size_hint_y=0.2))

        text_input = TextInput(
            hint_text="Type your answer...",
            font_size="20sp",
            multiline=False,
            size_hint_y=None,
            height=dp(50),
        )
        root.add_widget(text_input)

        submit_btn = Button(
            text="Check",
            font_size="18sp",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.345, 0.8, 0.008, 1),
            color=(1, 1, 1, 1),
        )
        submit_btn.bind(on_release=lambda *a: self._check_typing(ex, text_input.text, root))
        root.add_widget(submit_btn)

        root.add_widget(BoxLayout())  # spacer

    def _check_typing(self, ex, answer, root):
        correct = ex.check_answer(answer)
        self._show_feedback(root, correct, ex.correct_answer, ex)

    def _show_feedback(self, root, correct, correct_answer, ex):
        self.clear_widgets()
        feedback_root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))

        if correct:
            self._score += 1
            feedback_root.add_widget(Label(
                text="Correct!",
                font_size="32sp",
                bold=True,
                color=(0.345, 0.8, 0.008, 1),
            ))
        else:
            feedback_root.add_widget(Label(
                text="Incorrect",
                font_size="32sp",
                bold=True,
                color=(1, 0.294, 0.294, 1),
            ))
            feedback_root.add_widget(Label(
                text=f"Correct answer: {correct_answer}",
                font_size="20sp",
                color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None,
                height=dp(40),
            ))

        # Update SRS
        self._update_srs(ex, correct)

        feedback_root.add_widget(BoxLayout())  # spacer

        next_btn = Button(
            text="Next",
            font_size="20sp",
            size_hint_y=None,
            height=dp(55),
            background_color=(0.345, 0.8, 0.008, 1),
            color=(1, 1, 1, 1),
        )
        next_btn.bind(on_release=lambda *a: self._next())
        feedback_root.add_widget(next_btn)

        self.add_widget(feedback_root)

    def _update_srs(self, ex, correct):
        app = App.get_running_app()
        word = ex.word_sl
        state = app.progress.get_word_state(word)
        if state is None:
            state = WordState(word=word)
        state = self._srs.record_answer(state, correct)
        app.progress.update_word_state(state)

    def _next(self):
        self._current_idx += 1
        self._show_current()

    def _finish_lesson(self):
        app = App.get_running_app()
        app.progress.set_lesson_status(self.unit_id, "completed")
        app.progress.set_lesson_score(self.unit_id, self._score)
        results = self.manager.get_screen("results")
        results.unit_id = self.unit_id
        results.score = self._score
        results.total = len(self._exercises)
        self.manager.current = "results"
```

- [ ] **Step 2: Test locally — start a lesson and do exercises**

```bash
cd ~/Desktop/Slovenčk
uv run python src/main.py
```

Expected: Click "Continue Learning" → exercises render, can answer, see feedback, progress bar moves. Close window.

- [ ] **Step 3: Commit**

```bash
cd ~/Desktop/Slovenčk
git add src/screens/exercise.py
git commit -m "feat: add exercise screen with all 6 exercise type renderers"
```

---

### Task 13: Results Screen

**Files:**
- Create: `src/screens/results.py`

- [ ] **Step 1: Implement results screen**

```python
# src/screens/results.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
from kivy.metrics import dp


class ResultsScreen(Screen):
    unit_id = ""
    score = 0
    total = 10

    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()

        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))

        # Title
        root.add_widget(Label(
            text="Lesson Complete!",
            font_size="28sp",
            bold=True,
            color=(0.345, 0.8, 0.008, 1),
            size_hint_y=None,
            height=dp(50),
        ))

        # Score
        percentage = int((self.score / self.total) * 100) if self.total > 0 else 0
        score_color = (0.345, 0.8, 0.008, 1) if percentage >= 70 else (1, 0.6, 0, 1) if percentage >= 50 else (1, 0.294, 0.294, 1)
        root.add_widget(Label(
            text=f"{self.score} / {self.total}",
            font_size="48sp",
            bold=True,
            color=score_color,
            size_hint_y=None,
            height=dp(80),
        ))
        root.add_widget(Label(
            text=f"{percentage}%",
            font_size="24sp",
            color=score_color,
            size_hint_y=None,
            height=dp(40),
        ))

        # Words to review
        words_state = app.progress.get_words_state()
        unit_vocab = app.curriculum.get_vocab(self.unit_id)
        review_words = []
        for item in unit_vocab:
            state = words_state.get(item["sl"])
            if state and state.box == 1 and state.incorrect > 0:
                review_words.append(f"{item['sl']} = {item['en']}")

        if review_words:
            root.add_widget(Label(
                text="Words to review:",
                font_size="18sp",
                bold=True,
                color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None,
                height=dp(30),
            ))
            review_text = "\n".join(review_words[:5])
            root.add_widget(Label(
                text=review_text,
                font_size="16sp",
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height=dp(len(review_words[:5]) * 25),
                halign="center",
            ))

        root.add_widget(BoxLayout())  # spacer

        # Retry button
        retry_btn = Button(
            text="Retry Lesson",
            font_size="18sp",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        retry_btn.bind(on_release=self._retry)
        root.add_widget(retry_btn)

        # Continue button
        continue_btn = Button(
            text="Continue",
            font_size="18sp",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.345, 0.8, 0.008, 1),
            color=(1, 1, 1, 1),
        )
        continue_btn.bind(on_release=self._continue)
        root.add_widget(continue_btn)

        root.add_widget(BoxLayout(size_hint_y=None, height=dp(15)))
        self.add_widget(root)

    def _retry(self, *args):
        self.manager.get_screen("exercise").unit_id = self.unit_id
        self.manager.current = "exercise"

    def _continue(self, *args):
        self.manager.current = "lesson_select"
```

- [ ] **Step 2: Test locally — complete a full lesson flow**

```bash
cd ~/Desktop/Slovenčk
uv run python src/main.py
```

Expected: Home → Continue → do all 10 exercises → Results screen shows score, review words, retry/continue buttons. Close window.

- [ ] **Step 3: Commit**

```bash
cd ~/Desktop/Slovenčk
git add src/screens/results.py
git commit -m "feat: add results screen with score and review words"
```

---

### Task 14: Buildozer Config

**Files:**
- Create: `buildozer.spec`

- [ ] **Step 1: Create buildozer.spec**

```bash
cd ~/Desktop/Slovenčk
uv run buildozer init
```

- [ ] **Step 2: Edit buildozer.spec with correct values**

Modify the generated `buildozer.spec` to set these values:

```ini
[app]
title = Slovenčk
package.name = slovencek
package.domain = org.slovencek
source.dir = src
source.include_exts = py,png,jpg,kv,json,mp3
version = 0.1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[app:android]
presplash.filename = %(source.dir)s/assets/logo.png
icon.filename = %(source.dir)s/assets/logo.png
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.arch = arm64-v8a
```

- [ ] **Step 3: Commit**

```bash
cd ~/Desktop/Slovenčk
git add buildozer.spec
git commit -m "feat: add buildozer config for Android builds"
```

---

### Task 15: End-to-End Smoke Test

- [ ] **Step 1: Run all unit tests**

```bash
cd ~/Desktop/Slovenčk
uv run pytest tests/ -v
```

Expected: All tests pass (curriculum, SRS, progress, exercises, session).

- [ ] **Step 2: Run the app and complete a full lesson**

```bash
cd ~/Desktop/Slovenčk
uv run python src/main.py
```

Manual test:
1. Home screen shows stats (0/0/0)
2. Click "Continue Learning" → starts Pozdravi lesson
3. Complete all 10 exercises (mix of types)
4. Results screen shows score
5. Click "Continue" → Lesson Select shows Pozdravi as completed, Števila unlocked
6. Go back to Home → stats updated
7. Close app, reopen → progress persisted

- [ ] **Step 3: Generate audio (optional — needs internet)**

```bash
cd ~/Desktop/Slovenčk
uv run python scripts/generate_audio.py
```

Expected: .mp3 files appear in `src/audio/`.

- [ ] **Step 4: Generate assets (optional — needs GEMINI_API_KEY)**

```bash
cd ~/Desktop/Slovenčk
GEMINI_API_KEY=your-key-here uv run python scripts/generate_assets.py
```

Expected: .png files appear in `src/assets/`, `style.kv` in `src/theme/`.

- [ ] **Step 5: Final commit**

```bash
cd ~/Desktop/Slovenčk
git add -A
git commit -m "feat: Slovenčk v0.1.0 — complete language learning app"
```
