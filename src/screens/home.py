from pathlib import Path

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.app import App
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle

ASSETS_DIR = Path(__file__).parent.parent / "assets"


class HomeScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        stats = app.progress.get_stats()

        root = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(12))

        # Background
        with root.canvas.before:
            Color(0.969, 0.969, 0.969, 1)
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)

        # Top spacer
        root.add_widget(BoxLayout(size_hint_y=0.05))

        # Logo
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            logo = Image(
                source=str(logo_path),
                size_hint=(None, None),
                width=dp(100),
                height=dp(100),
                pos_hint={"center_x": 0.5},
            )
            root.add_widget(logo)

        # Title
        title = Label(
            text="Slovenčk",
            font_size="34sp",
            bold=True,
            color=(0.345, 0.8, 0.008, 1),
            size_hint_y=None,
            height=dp(45),
        )
        root.add_widget(title)

        # Subtitle
        subtitle = Label(
            text="Learn Slovenian",
            font_size="16sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(25),
        )
        root.add_widget(subtitle)

        root.add_widget(BoxLayout(size_hint_y=0.05))

        # Stats card
        stats_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(120), padding=dp(15), spacing=dp(5))
        with stats_box.canvas.before:
            Color(0, 0, 0, 0.04)
            self._stats_shadow = RoundedRectangle(pos=(stats_box.x + dp(1), stats_box.y - dp(2)), size=stats_box.size, radius=[dp(12)])
            Color(1, 1, 1, 1)
            self._stats_bg = RoundedRectangle(pos=stats_box.pos, size=stats_box.size, radius=[dp(12)])
        stats_box.bind(pos=self._update_stats_bg, size=self._update_stats_bg)

        stats_title = Label(
            text="Your Progress",
            font_size="16sp",
            bold=True,
            color=(0.345, 0.8, 0.008, 1),
            size_hint_y=None,
            height=dp(25),
            halign="center",
        )
        stats_title.bind(size=stats_title.setter("text_size"))
        stats_box.add_widget(stats_title)

        stats_items = [
            (f"{stats['lessons_completed']}", "Lessons"),
            (f"{stats['words_learned']}", "Learned"),
            (f"{stats['words_in_progress']}", "In Progress"),
        ]
        stats_row = BoxLayout(orientation="horizontal", spacing=dp(5))
        for number, label_text in stats_items:
            col = BoxLayout(orientation="vertical", spacing=dp(2))
            num = Label(text=number, font_size="26sp", bold=True, color=(0.2, 0.2, 0.2, 1), halign="center")
            num.bind(size=num.setter("text_size"))
            lbl = Label(text=label_text, font_size="12sp", color=(0.5, 0.5, 0.5, 1), halign="center")
            lbl.bind(size=lbl.setter("text_size"))
            col.add_widget(num)
            col.add_widget(lbl)
            stats_row.add_widget(col)
        stats_box.add_widget(stats_row)

        root.add_widget(stats_box)

        # Spacer
        root.add_widget(BoxLayout())

        # Continue button
        continue_btn = Button(
            text="Continue Learning",
            font_size="20sp",
            size_hint_y=None,
            height=dp(55),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            bold=True,
        )
        with continue_btn.canvas.before:
            Color(0.345, 0.8, 0.008, 1)
            self._btn1_bg = RoundedRectangle(pos=continue_btn.pos, size=continue_btn.size, radius=[dp(12)])
        continue_btn.bind(pos=self._update_btn1, size=self._update_btn1)
        continue_btn.bind(on_release=self._on_continue)
        root.add_widget(continue_btn)

        # Lesson select button
        select_btn = Button(
            text="All Lessons",
            font_size="18sp",
            size_hint_y=None,
            height=dp(50),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
        )
        with select_btn.canvas.before:
            Color(0.11, 0.69, 0.965, 1)
            self._btn2_bg = RoundedRectangle(pos=select_btn.pos, size=select_btn.size, radius=[dp(12)])
        select_btn.bind(pos=self._update_btn2, size=self._update_btn2)
        select_btn.bind(on_release=self._on_select)
        root.add_widget(select_btn)

        # Bottom spacer
        root.add_widget(BoxLayout(size_hint_y=None, height=dp(15)))

        self.add_widget(root)

    def _update_bg(self, instance, *args):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size

    def _update_stats_bg(self, instance, *args):
        self._stats_bg.pos = instance.pos
        self._stats_bg.size = instance.size
        self._stats_shadow.pos = (instance.x + 1, instance.y - 2)
        self._stats_shadow.size = instance.size

    def _update_btn1(self, instance, *args):
        self._btn1_bg.pos = instance.pos
        self._btn1_bg.size = instance.size

    def _update_btn2(self, instance, *args):
        self._btn2_bg.pos = instance.pos
        self._btn2_bg.size = instance.size

    def _on_continue(self, *args):
        app = App.get_running_app()
        units = app.curriculum.get_units()
        for unit in units:
            status = app.progress.get_lesson_status(unit["id"])
            if status != "completed":
                self.manager.get_screen("exercise").unit_id = unit["id"]
                self.manager.current = "exercise"
                return
        self.manager.current = "lesson_select"

    def _on_select(self, *args):
        self.manager.current = "lesson_select"
