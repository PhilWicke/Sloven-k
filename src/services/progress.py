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
