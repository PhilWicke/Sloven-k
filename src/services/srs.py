from dataclasses import dataclass
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
