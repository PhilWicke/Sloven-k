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
