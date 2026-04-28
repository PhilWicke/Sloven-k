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


def test_build_session_returns_exercises(builder):
    exercises = builder.build("pozdravi_1")
    assert len(exercises) == 10


def test_session_has_mixed_types(builder):
    exercises = builder.build("pozdravi_1")
    types = {ex.exercise_type for ex in exercises}
    assert len(types) >= 3


def test_no_two_same_types_in_a_row(builder):
    exercises = builder.build("pozdravi_1")
    for i in range(1, len(exercises)):
        assert exercises[i].exercise_type != exercises[i - 1].exercise_type


def test_due_words_prioritized(builder, progress):
    state = WordState(word="dober dan", box=1, last_reviewed=datetime.now() - timedelta(days=1))
    progress.update_word_state(state)
    exercises = builder.build("pozdravi_1")
    exercise_words = [ex.word_sl for ex in exercises]
    assert "dober dan" in exercise_words


def test_builds_for_any_unit(builder):
    exercises = builder.build("stevila_1")
    assert len(exercises) == 10


def test_review_builds_without_crash(builder, progress):
    # Mark some words as seen so review has data
    for word in ["dober dan", "živjo", "hvala"]:
        state = WordState(word=word, box=2, correct=1, incorrect=1)
        progress.update_word_state(state)
    exercises = builder.build("pozdravi_5")
    assert len(exercises) > 0
    assert len(exercises) <= 10
