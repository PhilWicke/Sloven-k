import pytest
from services.curriculum import CurriculumLoader


@pytest.fixture
def loader():
    return CurriculumLoader()


def test_load_returns_units(loader):
    units = loader.get_units()
    assert len(units) == 10
    assert units[0]["id"] == "pozdravi"
    assert units[0]["name_sl"] == "Pozdravi"
    assert units[0]["name_en"] == "Greetings"


def test_get_unit_vocab(loader):
    vocab = loader.get_vocab("pozdravi")
    assert len(vocab) >= 10
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
    sentences = loader.get_sentences("pozdravi")
    assert len(sentences) >= 2
    first = sentences[0]
    assert "sl" in first
    assert "en" in first
    assert "vocab_ids" in first


def test_all_units_have_vocab(loader):
    for unit in loader.get_units():
        vocab = loader.get_vocab(unit["id"])
        assert len(vocab) >= 5, f"Unit {unit['id']} has fewer than 5 vocab items"


def test_get_all_text_for_tts(loader):
    texts = loader.get_all_slovenian_texts()
    assert len(texts) > 50  # at least 50 unique Slovenian strings
    assert all(isinstance(t, str) for t in texts)
