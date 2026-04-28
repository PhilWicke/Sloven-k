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
