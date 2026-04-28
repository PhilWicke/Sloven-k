from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle

from exercises.base import ExerciseType
from exercises.session import SessionBuilder
from services.srs import SRSEngine, WordState
from services.audio import play_audio

# Earthy palette — darkened for contrast
BG = (0.96, 0.94, 0.91, 1)
CARD = (0.99, 0.97, 0.95, 1)
PRIMARY = (0.62, 0.32, 0.20, 1)       # darker terracotta
SECONDARY = (0.40, 0.48, 0.32, 1)     # darker sage
ACCENT = (0.52, 0.40, 0.30, 1)        # darker clay
TEXT_DARK = (0.15, 0.13, 0.11, 1)
TEXT_MID = (0.38, 0.34, 0.30, 1)
TEXT_LIGHT = (0.58, 0.54, 0.48, 1)
BTN_TEXT = (1.0, 0.98, 0.96, 1)
CORRECT = (0.38, 0.48, 0.26, 1)       # darker olive
ERROR = (0.70, 0.28, 0.22, 1)         # darker muted red
CHOICE_BG = (0.94, 0.91, 0.87, 1)     # slightly darker choice bg
PROGRESS_BG = (0.88, 0.86, 0.82, 1)
PROGRESS_FG = (0.62, 0.32, 0.20, 1)   # terracotta progress


def _make_btn(text, color, height=dp(48), font_size="16sp", bold=False):
    btn = Button(text=text, font_size=font_size, bold=bold,
                 size_hint_y=None, height=height,
                 background_normal="", background_down="",
                 background_color=(0, 0, 0, 0), color=BTN_TEXT)
    with btn.canvas.before:
        Color(*color)
        _r = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(8)])
    btn.bind(pos=lambda i, *a, r=_r: setattr(r, "pos", i.pos),
             size=lambda i, *a, r=_r: setattr(r, "size", i.size))
    return btn


def _make_choice_btn(text):
    btn = Button(text=text, font_size="16sp",
                 size_hint_y=None, height=dp(48),
                 background_normal="", background_down="",
                 background_color=(0, 0, 0, 0), color=TEXT_DARK)
    with btn.canvas.before:
        Color(*CHOICE_BG)
        _r = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(8)])
    btn.bind(pos=lambda i, *a, r=_r: setattr(r, "pos", i.pos),
             size=lambda i, *a, r=_r: setattr(r, "size", i.size))
    return btn


class ExerciseScreen(Screen):
    unit_id = ""

    def on_enter(self):
        app = App.get_running_app()
        builder = SessionBuilder(app.curriculum, app.progress)
        self._exercises = builder.build(self.unit_id)
        self._current_idx = 0
        self._score = 0
        self._srs = SRSEngine()
        self._show_current()

    def _make_root(self):
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(10))
        with root.canvas.before:
            Color(*BG)
            _r = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, *a: setattr(_r, "pos", i.pos),
                  size=lambda i, *a: setattr(_r, "size", i.size))
        return root

    def _show_current(self):
        self.clear_widgets()
        if self._current_idx >= len(self._exercises):
            self._finish_lesson()
            return

        ex = self._exercises[self._current_idx]
        root = self._make_root()

        # Progress bar (custom drawn)
        progress_box = BoxLayout(size_hint_y=None, height=dp(6))
        frac = self._current_idx / len(self._exercises) if self._exercises else 0
        with progress_box.canvas:
            Color(*PROGRESS_BG)
            self._prog_track = RoundedRectangle(pos=progress_box.pos, size=progress_box.size, radius=[dp(3)])
            Color(*PROGRESS_FG)
            self._prog_fill = RoundedRectangle(pos=progress_box.pos,
                                                size=(progress_box.width * frac, progress_box.height),
                                                radius=[dp(3)])
        def _upd_prog(inst, *a):
            self._prog_track.pos = inst.pos
            self._prog_track.size = inst.size
            self._prog_fill.pos = inst.pos
            self._prog_fill.size = (inst.width * frac, inst.height)
        progress_box.bind(pos=_upd_prog, size=_upd_prog)
        root.add_widget(progress_box)

        counter = Label(text=f"{self._current_idx + 1} / {len(self._exercises)}",
                        font_size="12sp", color=TEXT_LIGHT, size_hint_y=None, height=dp(20))
        root.add_widget(counter)

        if ex.exercise_type == ExerciseType.FLASHCARD:
            self._render_flashcard(root, ex)
        elif ex.exercise_type == ExerciseType.MULTIPLE_CHOICE:
            self._render_multiple_choice(root, ex)
        elif ex.exercise_type == ExerciseType.SENTENCE_BUILDING:
            self._render_sentence_building(root, ex)
        elif ex.exercise_type == ExerciseType.FILL_BLANK:
            self._render_fill_blank(root, ex)
        elif ex.exercise_type == ExerciseType.LISTENING:
            self._render_listening(root, ex)
        elif ex.exercise_type == ExerciseType.TYPING:
            self._render_typing(root, ex)

        self.add_widget(root)

    def _render_flashcard(self, root, ex):
        root.add_widget(Label(text="Flashcard", font_size="12sp", color=TEXT_LIGHT,
                              size_hint_y=None, height=dp(20)))
        root.add_widget(BoxLayout(size_hint_y=0.05))
        root.add_widget(Label(text=ex.word_sl, font_size="30sp", bold=True, color=TEXT_DARK))
        self._flash_answer = Label(text="tap to reveal", font_size="22sp", color=TEXT_LIGHT)
        root.add_widget(self._flash_answer)

        audio_btn = _make_btn("Play Audio", ACCENT, dp(40), "14sp")
        audio_btn.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(audio_btn)

        reveal_btn = _make_btn("Reveal", PRIMARY, dp(48), "17sp")

        def reveal(*args):
            self._flash_answer.text = ex.word_en
            self._flash_answer.color = TEXT_DARK
            reveal_btn.text = "I knew it"
            reveal_btn.unbind(on_release=reveal)
            reveal_btn.bind(on_release=lambda *a: self._record_and_next(ex, True))
            didnt = _make_btn("I didn't know", ERROR, dp(48), "17sp")
            didnt.bind(on_release=lambda *a: self._record_and_next(ex, False))
            root.add_widget(didnt)

        reveal_btn.bind(on_release=reveal)
        root.add_widget(reveal_btn)

    def _record_and_next(self, ex, correct):
        if correct:
            self._score += 1
        self._update_srs(ex, correct)
        self._current_idx += 1
        self._show_current()

    def _render_multiple_choice(self, root, ex):
        p = Label(text=ex.prompt, font_size="20sp", color=TEXT_DARK,
                  size_hint_y=None, height=dp(70), halign="center", valign="center")
        p.bind(size=p.setter("text_size"))
        root.add_widget(p)

        ab = _make_btn("Play Audio", ACCENT, dp(36), "13sp")
        ab.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(ab)
        root.add_widget(BoxLayout(size_hint_y=0.08))

        for i, choice in enumerate(ex.choices):
            btn = _make_choice_btn(choice)
            btn.bind(on_release=lambda inst, idx=i: self._check_mc(ex, idx, root))
            root.add_widget(btn)
            root.add_widget(BoxLayout(size_hint_y=None, height=dp(4)))

    def _check_mc(self, ex, selected, root):
        self._show_feedback(root, ex.check_answer(selected), ex.correct_answer, ex)

    def _render_sentence_building(self, root, ex):
        p = Label(text=ex.prompt, font_size="18sp", color=TEXT_DARK,
                  size_hint_y=None, height=dp(50), halign="center")
        p.bind(size=p.setter("text_size"))
        root.add_widget(p)

        self._sb_selected = []
        self._sb_answer_label = Label(text="···", font_size="18sp", color=PRIMARY,
                                      size_hint_y=None, height=dp(40))
        root.add_widget(self._sb_answer_label)
        root.add_widget(BoxLayout(size_hint_y=0.05))

        self._sb_tiles_box = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(140))
        self._sb_buttons = []
        for word in ex.scrambled_words:
            btn = _make_choice_btn(word)
            btn.bind(on_release=lambda inst, w=word: self._sb_tap(inst, w, ex, root))
            self._sb_buttons.append(btn)
            self._sb_tiles_box.add_widget(btn)
        root.add_widget(self._sb_tiles_box)

        clear = _make_btn("Clear", ACCENT, dp(36), "13sp")
        clear.bind(on_release=lambda *a: self._sb_clear())
        root.add_widget(clear)

    def _sb_tap(self, inst, word, ex, root):
        self._sb_selected.append(word)
        inst.disabled = True
        self._sb_answer_label.text = " ".join(self._sb_selected)
        if len(self._sb_selected) == len(ex.correct_words):
            self._show_feedback(root, ex.check_answer(self._sb_selected), ex.correct_answer, ex)

    def _sb_clear(self):
        self._sb_selected.clear()
        self._sb_answer_label.text = "···"
        for b in self._sb_buttons:
            b.disabled = False

    def _render_fill_blank(self, root, ex):
        root.add_widget(Label(text="Fill in the blank", font_size="12sp", color=TEXT_LIGHT,
                              size_hint_y=None, height=dp(20)))
        s = Label(text=ex.sentence_with_blank, font_size="18sp", color=TEXT_DARK,
                  size_hint_y=None, height=dp(50), halign="center")
        s.bind(size=s.setter("text_size"))
        root.add_widget(s)
        root.add_widget(BoxLayout(size_hint_y=0.08))

        for word in ex.word_bank:
            btn = _make_choice_btn(word)
            btn.bind(on_release=lambda inst, w=word: self._show_feedback(
                root, ex.check_answer(w), ex.correct_answer, ex))
            root.add_widget(btn)
            root.add_widget(BoxLayout(size_hint_y=None, height=dp(4)))

    def _render_listening(self, root, ex):
        root.add_widget(Label(text="What do you hear?", font_size="20sp", color=TEXT_DARK,
                              size_hint_y=None, height=dp(44)))
        ab = _make_btn("Play Audio", PRIMARY, dp(52), "18sp")
        ab.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(ab)
        Clock.schedule_once(lambda dt: play_audio(ex.word_sl), 0.5)
        root.add_widget(BoxLayout(size_hint_y=0.08))

        for i, choice in enumerate(ex.choices):
            btn = _make_choice_btn(choice)
            btn.bind(on_release=lambda inst, idx=i: self._show_feedback(
                root, ex.check_answer(idx), ex.correct_answer, ex))
            root.add_widget(btn)
            root.add_widget(BoxLayout(size_hint_y=None, height=dp(4)))

    def _render_typing(self, root, ex):
        p = Label(text=ex.prompt, font_size="20sp", color=TEXT_DARK,
                  size_hint_y=None, height=dp(50), halign="center")
        p.bind(size=p.setter("text_size"))
        root.add_widget(p)

        ab = _make_btn("Play Audio", ACCENT, dp(36), "13sp")
        ab.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(ab)
        root.add_widget(BoxLayout(size_hint_y=0.15))

        ti = TextInput(hint_text="Type your answer…", font_size="18sp", multiline=False,
                       size_hint_y=None, height=dp(48),
                       background_color=CARD, foreground_color=TEXT_DARK,
                       cursor_color=PRIMARY)
        root.add_widget(ti)
        root.add_widget(BoxLayout(size_hint_y=None, height=dp(6)))

        submit = _make_btn("Check", PRIMARY, dp(48), "17sp")
        submit.bind(on_release=lambda *a: self._show_feedback(
            root, ex.check_answer(ti.text), ex.correct_answer, ex))
        root.add_widget(submit)
        root.add_widget(BoxLayout())

    def _show_feedback(self, root, correct, correct_answer, ex):
        self.clear_widgets()
        fb = self._make_root()

        fb.add_widget(BoxLayout(size_hint_y=0.2))

        if correct:
            self._score += 1
            fb.add_widget(Label(text="Correct", font_size="28sp", bold=True, color=CORRECT))
        else:
            fb.add_widget(Label(text="Incorrect", font_size="28sp", bold=True, color=ERROR))
            fb.add_widget(Label(text=f"Answer: {correct_answer}", font_size="18sp",
                                color=TEXT_MID, size_hint_y=None, height=dp(36)))

        self._update_srs(ex, correct)
        fb.add_widget(BoxLayout())

        nxt = _make_btn("Next", PRIMARY, dp(50), "17sp")
        nxt.bind(on_release=lambda *a: self._next())
        fb.add_widget(nxt)
        fb.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))
        self.add_widget(fb)

    def _update_srs(self, ex, correct):
        app = App.get_running_app()
        state = app.progress.get_word_state(ex.word_sl)
        if state is None:
            state = WordState(word=ex.word_sl)
        state = self._srs.record_answer(state, correct)
        app.progress.update_word_state(state)

    def _next(self):
        self._current_idx += 1
        self._show_current()

    def _finish_lesson(self):
        app = App.get_running_app()
        app.progress.set_lesson_status(self.unit_id, "completed")
        app.progress.set_lesson_score(self.unit_id, self._score)
        results = self.manager.get_screen("results")
        results.unit_id = self.unit_id
        results.score = self._score
        results.total = len(self._exercises)
        self.manager.current = "results"
