import pytest
from services.curriculum import CurriculumLoader


@pytest.fixture
def loader():
    return CurriculumLoader()


def test_load_returns_units(loader):
    units = loader.get_units()
    assert len(units) == 50


def test_learning_units_have_10_vocab(loader):
    units = loader.get_units()
    learning = [u for u in units if not u.get("is_review")]
    assert len(learning) == 40
    for u in learning:
        vocab = loader.get_vocab(u["id"])
        assert len(vocab) == 10, f"Unit {u['id']} has {len(vocab)} vocab, expected 10"


def test_review_units_have_no_vocab(loader):
    units = loader.get_units()
    reviews = [u for u in units if u.get("is_review")]
    assert len(reviews) == 10
    for u in reviews:
        vocab = loader.get_vocab(u["id"])
        assert len(vocab) == 0, f"Review unit {u['id']} should have 0 vocab"


def test_get_unit_vocab(loader):
    vocab = loader.get_vocab("pozdravi_1")
    assert len(vocab) == 10
    first = vocab[0]
    assert "sl" in first
    assert "en" in first
    assert "phonetic" in first
    assert "example" in first
    assert "example_en" in first


def test_get_unit_vocab_invalid_unit(loader):
    with pytest.raises(KeyError):
        loader.get_vocab("nonexistent")


def test_get_sentences(loader):
    sentences = loader.get_sentences("pozdravi_1")
    assert len(sentences) >= 2
    first = sentences[0]
    assert "sl" in first
    assert "en" in first
    assert "vocab_ids" in first


def test_get_all_text_for_tts(loader):
    texts = loader.get_all_slovenian_texts()
    assert len(texts) > 200
    assert all(isinstance(t, str) for t in texts)
