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
    assert len(exercises) == 12  # min(SESSION_SIZE=20, vocab_count=12)


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
    assert len(exercises) == 12  # min(SESSION_SIZE=20, vocab_count=12)
