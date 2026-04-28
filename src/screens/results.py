from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
from kivy.metrics import dp


class ResultsScreen(Screen):
    unit_id = ""
    score = 0
    total = 10

    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()

        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))

        # Title
        root.add_widget(Label(
            text="Lesson Complete!",
            font_size="28sp",
            bold=True,
            color=(0.345, 0.8, 0.008, 1),
            size_hint_y=None,
            height=dp(50),
        ))

        # Score
        percentage = int((self.score / self.total) * 100) if self.total > 0 else 0
        score_color = (0.345, 0.8, 0.008, 1) if percentage >= 70 else (1, 0.6, 0, 1) if percentage >= 50 else (1, 0.294, 0.294, 1)
        root.add_widget(Label(
            text=f"{self.score} / {self.total}",
            font_size="48sp",
            bold=True,
            color=score_color,
            size_hint_y=None,
            height=dp(80),
        ))
        root.add_widget(Label(
            text=f"{percentage}%",
            font_size="24sp",
            color=score_color,
            size_hint_y=None,
            height=dp(40),
        ))

        # Words to review
        words_state = app.progress.get_words_state()
        unit_vocab = app.curriculum.get_vocab(self.unit_id)
        review_words = []
        for item in unit_vocab:
            state = words_state.get(item["sl"])
            if state and state.box == 1 and state.incorrect > 0:
                review_words.append(f"{item['sl']} = {item['en']}")

        if review_words:
            root.add_widget(Label(
                text="Words to review:",
                font_size="18sp",
                bold=True,
                color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None,
                height=dp(30),
            ))
            review_text = "\n".join(review_words[:5])
            review_label = Label(
                text=review_text,
                font_size="16sp",
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height=dp(len(review_words[:5]) * 25),
                halign="center",
            )
            review_label.bind(size=review_label.setter("text_size"))
            root.add_widget(review_label)

        root.add_widget(BoxLayout())  # spacer

        # Retry button
        retry_btn = Button(
            text="Retry Lesson",
            font_size="18sp",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        retry_btn.bind(on_release=self._retry)
        root.add_widget(retry_btn)

        # Continue button
        continue_btn = Button(
            text="Continue",
            font_size="18sp",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.345, 0.8, 0.008, 1),
            color=(1, 1, 1, 1),
        )
        continue_btn.bind(on_release=self._continue)
        root.add_widget(continue_btn)

        root.add_widget(BoxLayout(size_hint_y=None, height=dp(15)))
        self.add_widget(root)

    def _retry(self, *args):
        self.manager.get_screen("exercise").unit_id = self.unit_id
        self.manager.current = "exercise"

    def _continue(self, *args):
        self.manager.current = "lesson_select"
