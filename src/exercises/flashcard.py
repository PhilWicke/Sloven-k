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
