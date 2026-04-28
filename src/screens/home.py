from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
from kivy.metrics import dp


class HomeScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        stats = app.progress.get_stats()

        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))

        # Title
        title = Label(
            text="Slovenčk",
            font_size="36sp",
            bold=True,
            color=(0.345, 0.8, 0.008, 1),
            size_hint_y=None,
            height=dp(60),
        )
        root.add_widget(title)

        # Subtitle
        subtitle = Label(
            text="Learn Slovenian",
            font_size="18sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(30),
        )
        root.add_widget(subtitle)

        # Stats
        stats_text = (
            f"Lessons completed: {stats['lessons_completed']}\n"
            f"Words learned: {stats['words_learned']}\n"
            f"Words in progress: {stats['words_in_progress']}"
        )
        stats_label = Label(
            text=stats_text,
            font_size="18sp",
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(100),
            halign="center",
        )
        stats_label.bind(size=stats_label.setter("text_size"))
        root.add_widget(stats_label)

        # Spacer
        root.add_widget(BoxLayout())

        # Continue button
        continue_btn = Button(
            text="Continue Learning",
            font_size="20sp",
            size_hint_y=None,
            height=dp(55),
            background_color=(0.345, 0.8, 0.008, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        continue_btn.bind(on_release=self._on_continue)
        root.add_widget(continue_btn)

        # Lesson select button
        select_btn = Button(
            text="All Lessons",
            font_size="18sp",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.11, 0.69, 0.965, 1),
            color=(1, 1, 1, 1),
        )
        select_btn.bind(on_release=self._on_select)
        root.add_widget(select_btn)

        # Bottom spacer
        root.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))

        self.add_widget(root)

    def _on_continue(self, *args):
        app = App.get_running_app()
        units = app.curriculum.get_units()
        # Find first incomplete lesson
        for unit in units:
            status = app.progress.get_lesson_status(unit["id"])
            if status != "completed":
                self.manager.get_screen("exercise").unit_id = unit["id"]
                self.manager.current = "exercise"
                return
        # All done — go to lesson select
        self.manager.current = "lesson_select"

    def _on_select(self, *args):
        self.manager.current = "lesson_select"
