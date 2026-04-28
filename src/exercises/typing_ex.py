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
