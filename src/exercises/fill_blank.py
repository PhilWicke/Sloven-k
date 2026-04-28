from dataclasses import dataclass
from exercises.base import ExerciseType
from exercises.matching import answers_match


@dataclass
class FillBlankExercise:
    sentence_with_blank: str
    correct_answer: str
    word_bank: list[str]
    word_sl: str
    exercise_type: ExerciseType = ExerciseType.FILL_BLANK

    def check_answer(self, answer: str) -> bool:
        return answers_match(answer, self.correct_answer)
