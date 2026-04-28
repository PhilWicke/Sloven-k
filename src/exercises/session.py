import random
import hashlib
from exercises.base import ExerciseType
from exercises.flashcard import FlashcardExercise
from exercises.multiple_choice import MultipleChoiceExercise
from exercises.sentence_building import SentenceBuildingExercise
from exercises.fill_blank import FillBlankExercise
from exercises.listening import ListeningExercise
from exercises.typing_ex import TypingExercise
from services.curriculum import CurriculumLoader
from services.progress import ProgressManager
from services.srs import SRSEngine, WordState

SESSION_SIZE = 20


def _audio_path(text: str) -> str:
    h = hashlib.md5(text.encode()).hexdigest()
    return f"{h}.mp3"


class SessionBuilder:
    def __init__(self, curriculum: CurriculumLoader, progress: ProgressManager):
        self._curriculum = curriculum
        self._progress = progress
        self._srs = SRSEngine()

    def build(self, unit_id: str) -> list:
        vocab = self._curriculum.get_vocab(unit_id)
        sentences = self._curriculum.get_sentences(unit_id)
        words_state = self._progress.get_words_state()
        session_size = min(SESSION_SIZE, len(vocab))

        # Separate due words and new words
        due_words = []
        new_words = []
        for item in vocab:
            state = words_state.get(item["sl"])
            if state and self._srs.is_due(state):
                due_words.append(item)
            elif state is None:
                new_words.append(item)

        # Pick words for this session: due first, then new — no duplicates
        selected = []
        seen_words = set()

        for item in due_words:
            if item["sl"] not in seen_words and len(selected) < session_size:
                selected.append(item)
                seen_words.add(item["sl"])

        random.shuffle(new_words)
        for item in new_words:
            if item["sl"] not in seen_words and len(selected) < session_size:
                selected.append(item)
                seen_words.add(item["sl"])

        # If still not enough, add non-due reviewed words
        if len(selected) < session_size:
            reviewed = [v for v in vocab if v["sl"] not in seen_words]
            random.shuffle(reviewed)
            for item in reviewed:
                if len(selected) >= session_size:
                    break
                selected.append(item)
                seen_words.add(item["sl"])

        # Build exercises with mixed types, no two same in a row
        all_vocab_words = [v["en"] for v in vocab]
        all_sl_words = [v["sl"] for v in vocab]
        exercise_types = [
            ExerciseType.FLASHCARD,
            ExerciseType.MULTIPLE_CHOICE,
            ExerciseType.SENTENCE_BUILDING,
            ExerciseType.FILL_BLANK,
            ExerciseType.LISTENING,
            ExerciseType.TYPING,
        ]

        exercises = []
        last_type = None
        for item in selected:
            available = [t for t in exercise_types if t != last_type]

            # Sentence building needs a sentence — only use if we have one
            item_sentences = [s for s in sentences if item["sl"] in s.get("vocab_ids", [])]
            if not item_sentences:
                available = [t for t in available if t != ExerciseType.SENTENCE_BUILDING]

            chosen_type = random.choice(available)
            ex = self._create_exercise(chosen_type, item, all_vocab_words, all_sl_words, item_sentences)
            exercises.append(ex)
            last_type = chosen_type

        return exercises

    def _create_exercise(self, ex_type: ExerciseType, item: dict, all_en_words: list[str], all_sl_words: list[str], sentences: list[dict]):
        word_sl = item["sl"]
        word_en = item["en"]
        audio = _audio_path(word_sl)

        if ex_type == ExerciseType.FLASHCARD:
            return FlashcardExercise(word_sl=word_sl, word_en=word_en, audio_file=audio)

        elif ex_type == ExerciseType.MULTIPLE_CHOICE:
            distractors = [w for w in all_en_words if w != word_en]
            random.shuffle(distractors)
            choices = distractors[:3] + [word_en]
            random.shuffle(choices)
            return MultipleChoiceExercise(
                prompt=f"What is '{word_sl}' in English?",
                choices=choices,
                correct_index=choices.index(word_en),
                word_sl=word_sl,
            )

        elif ex_type == ExerciseType.SENTENCE_BUILDING:
            sent = random.choice(sentences)
            words = sent["sl"].split()
            scrambled = words[:]
            while scrambled == words and len(words) > 1:
                random.shuffle(scrambled)
            return SentenceBuildingExercise(
                prompt=f"Build: '{sent['en']}'",
                correct_words=words,
                scrambled_words=scrambled,
                word_sl=word_sl,
            )

        elif ex_type == ExerciseType.FILL_BLANK:
            sentence = item["example"]
            blank_sentence = sentence.replace(word_sl, "_____", 1)
            if blank_sentence == sentence:
                blank_sentence = f"_____ = {word_en}"
            distractors = [w for w in all_sl_words if w != word_sl]
            random.shuffle(distractors)
            word_bank = distractors[:3] + [word_sl]
            random.shuffle(word_bank)
            return FillBlankExercise(
                sentence_with_blank=blank_sentence,
                correct_answer=word_sl,
                word_bank=word_bank,
                word_sl=word_sl,
            )

        elif ex_type == ExerciseType.LISTENING:
            distractors = [w for w in all_sl_words if w != word_sl]
            random.shuffle(distractors)
            choices = distractors[:3] + [word_sl]
            random.shuffle(choices)
            return ListeningExercise(
                audio_file=audio,
                choices=choices,
                correct_index=choices.index(word_sl),
                word_sl=word_sl,
            )

        elif ex_type == ExerciseType.TYPING:
            return TypingExercise(
                prompt=f"Type the English for: {word_sl}",
                correct_answer=word_en,
                word_sl=word_sl,
            )
