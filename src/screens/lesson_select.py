from pathlib import Path

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.app import App
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

ASSETS_DIR = Path(__file__).parent.parent / "assets"


class LessonCard(BoxLayout):
    def __init__(self, unit, status, score, locked, on_tap, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(80)
        self.padding = dp(12)
        self.spacing = dp(12)

        # Background with shadow
        with self.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.05)
            self._shadow = RoundedRectangle(pos=(self.x + dp(1), self.y - dp(2)), size=self.size, radius=[dp(12)])
            # Card
            if locked:
                Color(0.92, 0.92, 0.92, 1)
            elif status == "completed":
                Color(0.92, 0.98, 0.88, 1)
            else:
                Color(1, 1, 1, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Unit icon
        icon_path = ASSETS_DIR / f"icon_{unit['id']}.png"
        if icon_path.exists():
            icon = Image(
                source=str(icon_path),
                size_hint=(None, None),
                width=dp(50),
                height=dp(50),
                pos_hint={"center_y": 0.5},
            )
            self.add_widget(icon)

        # Text info
        text_box = BoxLayout(orientation="vertical", spacing=dp(2))
        name_label = Label(
            text=f"{unit['name_sl']} / {unit['name_en']}",
            font_size="17sp",
            bold=True,
            color=(0.6, 0.6, 0.6, 1) if locked else (0.15, 0.15, 0.15, 1),
            halign="left",
            valign="center",
            size_hint_x=1,
        )
        name_label.bind(size=name_label.setter("text_size"))
        text_box.add_widget(name_label)

        status_text = "Locked" if locked else status.replace("_", " ").title()
        if score > 0:
            status_text += f" (Best: {score}/10)"
        status_label = Label(
            text=status_text,
            font_size="14sp",
            color=(0.6, 0.6, 0.6, 1),
            halign="left",
            valign="center",
        )
        status_label.bind(size=status_label.setter("text_size"))
        text_box.add_widget(status_label)

        self.add_widget(text_box)

        if not locked:
            # Make it tappable
            btn = Button(
                text="Start" if status == "not_started" else "Continue" if status == "in_progress" else "Review",
                font_size="14sp",
                size_hint=(None, None),
                width=dp(70),
                height=dp(40),
                pos_hint={"center_y": 0.5},
                background_color=(0.345, 0.8, 0.008, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(on_release=lambda *a: on_tap(unit["id"]))
            self.add_widget(btn)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._shadow.pos = (self.x + 1, self.y - 2)
        self._shadow.size = self.size


class LessonSelectScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        units = app.curriculum.get_units()

        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(
            text="<",
            size_hint=(None, None),
            width=dp(40),
            height=dp(40),
            font_size="20sp",
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0.2, 0.2, 0.2, 1),
        )
        back_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "home"))
        header.add_widget(back_btn)
        header.add_widget(Label(
            text="Lessons",
            font_size="24sp",
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
        ))
        root.add_widget(header)

        # Scrollable lesson list
        scroll = ScrollView()
        lesson_list = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        lesson_list.bind(minimum_height=lesson_list.setter("height"))

        prev_completed = True  # first lesson is always unlocked
        for unit in units:
            status = app.progress.get_lesson_status(unit["id"])
            score = app.progress.get_lesson_score(unit["id"])
            locked = not prev_completed
            card = LessonCard(
                unit=unit,
                status=status,
                score=score,
                locked=locked,
                on_tap=self._start_lesson,
            )
            lesson_list.add_widget(card)
            if status == "completed":
                prev_completed = True
            else:
                prev_completed = False

        scroll.add_widget(lesson_list)
        root.add_widget(scroll)
        self.add_widget(root)

    def _start_lesson(self, unit_id):
        self.manager.get_screen("exercise").unit_id = unit_id
        self.manager.current = "exercise"
