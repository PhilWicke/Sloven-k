import pytest
from datetime import datetime, timedelta
from services.srs import SRSEngine, WordState


def test_new_word_starts_in_box_1():
    state = WordState(word="hvala")
    assert state.box == 1
    assert state.correct == 0
    assert state.incorrect == 0


def test_correct_answer_moves_up():
    engine = SRSEngine()
    state = WordState(word="hvala", box=1)
    state = engine.record_answer(state, correct=True)
    assert state.box == 2
    assert state.correct == 1


def test_incorrect_answer_resets_to_box_1():
    engine = SRSEngine()
    state = WordState(word="hvala", box=3)
    state = engine.record_answer(state, correct=False)
    assert state.box == 1
    assert state.incorrect == 1


def test_box_5_is_max():
    engine = SRSEngine()
    state = WordState(word="hvala", box=5)
    state = engine.record_answer(state, correct=True)
    assert state.box == 5


def test_is_due_box_1_always_due():
    engine = SRSEngine()
    state = WordState(word="hvala", box=1, last_reviewed=datetime.now())
    assert engine.is_due(state) is True


def test_is_due_box_2_after_1_day():
    engine = SRSEngine()
    state = WordState(word="hvala", box=2, last_reviewed=datetime.now() - timedelta(days=2))
    assert engine.is_due(state) is True


def test_is_not_due_box_2_same_day():
    engine = SRSEngine()
    state = WordState(word="hvala", box=2, last_reviewed=datetime.now())
    assert engine.is_due(state) is False


def test_is_due_box_5_after_14_days():
    engine = SRSEngine()
    state = WordState(word="hvala", box=5, last_reviewed=datetime.now() - timedelta(days=15))
    assert engine.is_due(state) is True


def test_is_learned():
    engine = SRSEngine()
    state = WordState(word="hvala", box=5)
    assert engine.is_learned(state) is True
    state2 = WordState(word="hvala", box=3)
    assert engine.is_learned(state2) is False


def test_word_state_to_dict_roundtrip():
    state = WordState(word="hvala", box=3, correct=5, incorrect=2, last_reviewed=datetime(2026, 4, 28, 12, 0, 0))
    d = state.to_dict()
    restored = WordState.from_dict(d)
    assert restored.word == state.word
    assert restored.box == state.box
    assert restored.correct == state.correct
    assert restored.incorrect == state.incorrect
    assert restored.last_reviewed == state.last_reviewed
