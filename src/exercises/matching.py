"""Fuzzy answer matching for exercise types."""
import re
import unicodedata


def normalize(text: str) -> str:
    """Normalize text for comparison: lowercase, strip, collapse whitespace, remove punctuation."""
    text = text.strip().lower()
    text = re.sub(r"[.,!?;:\"'()—–-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def answers_match(user_answer: str, correct_answer: str) -> bool:
    """Check if user answer matches correct answer with fuzzy tolerance."""
    if normalize(user_answer) == normalize(correct_answer):
        return True

    # Also try without accents (common for learners typing on English keyboards)
    def strip_accents(s):
        return "".join(
            c for c in unicodedata.normalize("NFD", s)
            if unicodedata.category(c) != "Mn"
        )

    if strip_accents(normalize(user_answer)) == strip_accents(normalize(correct_answer)):
        return True

    return False
