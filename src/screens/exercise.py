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

from exercises.base import ExerciseType
from exercises.session import SessionBuilder
from services.srs import SRSEngine, WordState
from services.audio import play_audio


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

    def _show_current(self):
        self.clear_widgets()
        if self._current_idx >= len(self._exercises):
            self._finish_lesson()
            return

        ex = self._exercises[self._current_idx]
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))

        # Progress bar
        progress = ProgressBar(
            max=len(self._exercises),
            value=self._current_idx,
            size_hint_y=None,
            height=dp(8),
        )
        root.add_widget(progress)

        # Counter
        counter = Label(
            text=f"{self._current_idx + 1} / {len(self._exercises)}",
            font_size="14sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(25),
        )
        root.add_widget(counter)

        # Render by type
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
        root.add_widget(Label(
            text="Flashcard",
            font_size="16sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(25),
        ))

        # Card area
        card_box = BoxLayout(orientation="vertical", spacing=dp(10))

        word_label = Label(
            text=ex.word_sl,
            font_size="32sp",
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
        )
        card_box.add_widget(word_label)

        self._flash_answer = Label(
            text="Tap to reveal",
            font_size="24sp",
            color=(0.6, 0.6, 0.6, 1),
        )
        card_box.add_widget(self._flash_answer)

        root.add_widget(card_box)

        # Audio button
        audio_btn = Button(
            text="Play Audio",
            size_hint_y=None,
            height=dp(45),
            font_size="16sp",
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        audio_btn.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(audio_btn)

        # Reveal button
        reveal_btn = Button(
            text="Reveal Translation",
            size_hint_y=None,
            height=dp(50),
            font_size="18sp",
            background_color=(0.345, 0.8, 0.008, 1),
            color=(1, 1, 1, 1),
        )

        def reveal(*args):
            self._flash_answer.text = ex.word_en
            self._flash_answer.color = (0.2, 0.2, 0.2, 1)
            reveal_btn.text = "I knew it!"
            reveal_btn.unbind(on_release=reveal)
            reveal_btn.bind(on_release=lambda *a: self._record_and_next(ex, True))
            # Add "I didn't know" button
            didnt_btn = Button(
                text="I didn't know",
                size_hint_y=None,
                height=dp(50),
                font_size="18sp",
                background_color=(1, 0.294, 0.294, 1),
                color=(1, 1, 1, 1),
            )
            didnt_btn.bind(on_release=lambda *a: self._record_and_next(ex, False))
            root.add_widget(didnt_btn)

        reveal_btn.bind(on_release=reveal)
        root.add_widget(reveal_btn)

    def _record_and_next(self, ex, correct):
        if correct:
            self._score += 1
        self._update_srs(ex, correct)
        self._current_idx += 1
        self._show_current()

    def _render_multiple_choice(self, root, ex):
        prompt_label = Label(
            text=ex.prompt,
            font_size="22sp",
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(80),
            halign="center",
            valign="center",
        )
        prompt_label.bind(size=prompt_label.setter("text_size"))
        root.add_widget(prompt_label)

        # Audio
        audio_btn = Button(
            text="Play Audio",
            size_hint_y=None,
            height=dp(40),
            font_size="14sp",
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        audio_btn.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(audio_btn)

        root.add_widget(BoxLayout(size_hint_y=0.1))  # spacer

        for i, choice in enumerate(ex.choices):
            btn = Button(
                text=choice,
                font_size="18sp",
                size_hint_y=None,
                height=dp(50),
                background_color=(0.95, 0.95, 0.95, 1),
                color=(0.2, 0.2, 0.2, 1),
            )
            btn.bind(on_release=lambda inst, idx=i: self._check_mc(ex, idx, root))
            root.add_widget(btn)

    def _check_mc(self, ex, selected, root):
        correct = ex.check_answer(selected)
        self._show_feedback(root, correct, ex.correct_answer, ex)

    def _render_sentence_building(self, root, ex):
        prompt_label = Label(
            text=ex.prompt,
            font_size="20sp",
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(60),
            halign="center",
        )
        prompt_label.bind(size=prompt_label.setter("text_size"))
        root.add_widget(prompt_label)

        # Answer area
        self._sb_selected = []
        self._sb_answer_label = Label(
            text="...",
            font_size="20sp",
            color=(0.345, 0.8, 0.008, 1),
            size_hint_y=None,
            height=dp(50),
        )
        root.add_widget(self._sb_answer_label)

        root.add_widget(BoxLayout(size_hint_y=0.1))

        # Word tiles
        self._sb_tiles_box = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(150))
        self._sb_buttons = []
        for word in ex.scrambled_words:
            btn = Button(
                text=word,
                font_size="16sp",
                size_hint_y=None,
                height=dp(45),
                background_color=(0.11, 0.69, 0.965, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(on_release=lambda inst, w=word: self._sb_tap(inst, w, ex, root))
            self._sb_buttons.append(btn)
            self._sb_tiles_box.add_widget(btn)
        root.add_widget(self._sb_tiles_box)

        # Clear button
        clear_btn = Button(
            text="Clear",
            size_hint_y=None,
            height=dp(40),
            font_size="14sp",
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0.2, 0.2, 0.2, 1),
        )
        clear_btn.bind(on_release=lambda *a: self._sb_clear())
        root.add_widget(clear_btn)

    def _sb_tap(self, btn_inst, word, ex, root):
        self._sb_selected.append(word)
        btn_inst.disabled = True
        self._sb_answer_label.text = " ".join(self._sb_selected)
        if len(self._sb_selected) == len(ex.correct_words):
            correct = ex.check_answer(self._sb_selected)
            self._show_feedback(root, correct, ex.correct_answer, ex)

    def _sb_clear(self):
        self._sb_selected.clear()
        self._sb_answer_label.text = "..."
        for btn in self._sb_buttons:
            btn.disabled = False

    def _render_fill_blank(self, root, ex):
        root.add_widget(Label(
            text="Fill in the blank:",
            font_size="16sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(25),
        ))
        sentence_label = Label(
            text=ex.sentence_with_blank,
            font_size="20sp",
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(60),
            halign="center",
        )
        sentence_label.bind(size=sentence_label.setter("text_size"))
        root.add_widget(sentence_label)

        root.add_widget(BoxLayout(size_hint_y=0.1))

        for word in ex.word_bank:
            btn = Button(
                text=word,
                font_size="18sp",
                size_hint_y=None,
                height=dp(50),
                background_color=(0.95, 0.95, 0.95, 1),
                color=(0.2, 0.2, 0.2, 1),
            )
            btn.bind(on_release=lambda inst, w=word: self._check_fill(ex, w, root))
            root.add_widget(btn)

    def _check_fill(self, ex, answer, root):
        correct = ex.check_answer(answer)
        self._show_feedback(root, correct, ex.correct_answer, ex)

    def _render_listening(self, root, ex):
        root.add_widget(Label(
            text="What do you hear?",
            font_size="22sp",
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(50),
        ))

        # Play audio button (big)
        audio_btn = Button(
            text="Play Audio",
            font_size="20sp",
            size_hint_y=None,
            height=dp(60),
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        audio_btn.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(audio_btn)

        # Auto-play on enter
        Clock.schedule_once(lambda dt: play_audio(ex.word_sl), 0.5)

        root.add_widget(BoxLayout(size_hint_y=0.1))

        for i, choice in enumerate(ex.choices):
            btn = Button(
                text=choice,
                font_size="18sp",
                size_hint_y=None,
                height=dp(50),
                background_color=(0.95, 0.95, 0.95, 1),
                color=(0.2, 0.2, 0.2, 1),
            )
            btn.bind(on_release=lambda inst, idx=i: self._check_listening(ex, idx, root))
            root.add_widget(btn)

    def _check_listening(self, ex, selected, root):
        correct = ex.check_answer(selected)
        self._show_feedback(root, correct, ex.correct_answer, ex)

    def _render_typing(self, root, ex):
        prompt_label = Label(
            text=ex.prompt,
            font_size="22sp",
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(60),
            halign="center",
        )
        prompt_label.bind(size=prompt_label.setter("text_size"))
        root.add_widget(prompt_label)

        # Audio
        audio_btn = Button(
            text="Play Audio",
            size_hint_y=None,
            height=dp(40),
            font_size="14sp",
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        audio_btn.bind(on_release=lambda *a: play_audio(ex.word_sl))
        root.add_widget(audio_btn)

        root.add_widget(BoxLayout(size_hint_y=0.2))

        text_input = TextInput(
            hint_text="Type your answer...",
            font_size="20sp",
            multiline=False,
            size_hint_y=None,
            height=dp(50),
        )
        root.add_widget(text_input)

        submit_btn = Button(
            text="Check",
            font_size="18sp",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.345, 0.8, 0.008, 1),
            color=(1, 1, 1, 1),
        )
        submit_btn.bind(on_release=lambda *a: self._check_typing(ex, text_input.text, root))
        root.add_widget(submit_btn)

        root.add_widget(BoxLayout())  # spacer

    def _check_typing(self, ex, answer, root):
        correct = ex.check_answer(answer)
        self._show_feedback(root, correct, ex.correct_answer, ex)

    def _show_feedback(self, root, correct, correct_answer, ex):
        self.clear_widgets()
        feedback_root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))

        if correct:
            self._score += 1
            feedback_root.add_widget(Label(
                text="Correct!",
                font_size="32sp",
                bold=True,
                color=(0.345, 0.8, 0.008, 1),
            ))
        else:
            feedback_root.add_widget(Label(
                text="Incorrect",
                font_size="32sp",
                bold=True,
                color=(1, 0.294, 0.294, 1),
            ))
            feedback_root.add_widget(Label(
                text=f"Correct answer: {correct_answer}",
                font_size="20sp",
                color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None,
                height=dp(40),
            ))

        # Update SRS
        self._update_srs(ex, correct)

        feedback_root.add_widget(BoxLayout())  # spacer

        next_btn = Button(
            text="Next",
            font_size="20sp",
            size_hint_y=None,
            height=dp(55),
            background_color=(0.345, 0.8, 0.008, 1),
            color=(1, 1, 1, 1),
        )
        next_btn.bind(on_release=lambda *a: self._next())
        feedback_root.add_widget(next_btn)

        self.add_widget(feedback_root)

    def _update_srs(self, ex, correct):
        app = App.get_running_app()
        word = ex.word_sl
        state = app.progress.get_word_state(word)
        if state is None:
            state = WordState(word=word)
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
