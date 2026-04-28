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
