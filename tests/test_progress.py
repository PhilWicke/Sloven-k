import pytest
import json
from pathlib import Path
from services.progress import ProgressManager


@pytest.fixture
def tmp_progress(tmp_path):
    return ProgressManager(tmp_path / "progress.json")


def test_fresh_progress_has_empty_state(tmp_progress):
    assert tmp_progress.get_lesson_status("pozdravi") == "not_started"
    assert tmp_progress.get_words_state() == {}


def test_set_lesson_status(tmp_progress):
    tmp_progress.set_lesson_status("pozdravi", "in_progress")
    assert tmp_progress.get_lesson_status("pozdravi") == "in_progress"


def test_set_lesson_score(tmp_progress):
    tmp_progress.set_lesson_score("pozdravi", 8)
    assert tmp_progress.get_lesson_score("pozdravi") == 8
    tmp_progress.set_lesson_score("pozdravi", 6)
    assert tmp_progress.get_lesson_score("pozdravi") == 8  # keeps best


def test_update_word_state(tmp_progress):
    from services.srs import WordState
    state = WordState(word="hvala", box=2, correct=3, incorrect=1)
    tmp_progress.update_word_state(state)
    loaded = tmp_progress.get_word_state("hvala")
    assert loaded.box == 2
    assert loaded.correct == 3


def test_save_and_load(tmp_progress, tmp_path):
    from services.srs import WordState
    tmp_progress.set_lesson_status("pozdravi", "completed")
    tmp_progress.set_lesson_score("pozdravi", 9)
    tmp_progress.update_word_state(WordState(word="hvala", box=3, correct=5, incorrect=1))
    tmp_progress.save()

    loaded = ProgressManager(tmp_path / "progress.json")
    assert loaded.get_lesson_status("pozdravi") == "completed"
    assert loaded.get_lesson_score("pozdravi") == 9
    assert loaded.get_word_state("hvala").box == 3


def test_stats(tmp_progress):
    from services.srs import WordState
    tmp_progress.set_lesson_status("pozdravi", "completed")
    tmp_progress.set_lesson_status("stevila", "completed")
    tmp_progress.update_word_state(WordState(word="hvala", box=5))
    tmp_progress.update_word_state(WordState(word="da", box=3))
    stats = tmp_progress.get_stats()
    assert stats["lessons_completed"] == 2
    assert stats["words_learned"] == 1
    assert stats["words_in_progress"] == 1
