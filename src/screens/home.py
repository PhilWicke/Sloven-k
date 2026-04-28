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

# Earthy palette — darkened for contrast
BG = (0.96, 0.94, 0.91, 1)
CARD = (0.99, 0.97, 0.95, 1)
PRIMARY = (0.62, 0.32, 0.20, 1)
SECONDARY = (0.40, 0.48, 0.32, 1)
TEXT_DARK = (0.15, 0.13, 0.11, 1)
TEXT_MID = (0.38, 0.34, 0.30, 1)
TEXT_LIGHT = (0.58, 0.54, 0.48, 1)
BTN_TEXT = (1.0, 0.98, 0.96, 1)


class HomeScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        stats = app.progress.get_stats()

        root = BoxLayout(orientation="vertical", padding=dp(28), spacing=dp(14))
        with root.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, *a: setattr(self._bg, "pos", i.pos),
                  size=lambda i, *a: setattr(self._bg, "size", i.size))

        root.add_widget(BoxLayout(size_hint_y=0.06))

        # Logo
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            root.add_widget(Image(source=str(logo_path), size_hint=(None, None),
                                  width=dp(80), height=dp(80), pos_hint={"center_x": 0.5}))

        # Title
        root.add_widget(Label(text="Slovenčk", font_size="30sp", bold=True,
                              color=TEXT_DARK, size_hint_y=None, height=dp(40)))
        root.add_widget(Label(text="Learn Slovenian", font_size="14sp",
                              color=TEXT_LIGHT, size_hint_y=None, height=dp(20)))

        root.add_widget(BoxLayout(size_hint_y=0.04))

        # Stats card
        stats_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(110),
                              padding=dp(16), spacing=dp(6))
        with stats_box.canvas.before:
            Color(0, 0, 0, 0.025)
            self._ss = RoundedRectangle(pos=stats_box.pos, size=stats_box.size, radius=[dp(8)])
            Color(*CARD)
            self._sb = RoundedRectangle(pos=stats_box.pos, size=stats_box.size, radius=[dp(8)])
        stats_box.bind(
            pos=lambda i, *a: (setattr(self._sb, "pos", i.pos), setattr(self._ss, "pos", (i.x+1, i.y-1))),
            size=lambda i, *a: (setattr(self._sb, "size", i.size), setattr(self._ss, "size", i.size)))

        st = Label(text="Your Progress", font_size="13sp", bold=True,
                   color=PRIMARY, size_hint_y=None, height=dp(22), halign="center")
        st.bind(size=st.setter("text_size"))
        stats_box.add_widget(st)

        row = BoxLayout(spacing=dp(5))
        for num, lbl in [(f"{stats['lessons_completed']}", "Lessons"),
                         (f"{stats['words_learned']}", "Learned"),
                         (f"{stats['words_in_progress']}", "Reviewing")]:
            col = BoxLayout(orientation="vertical", spacing=dp(1))
            n = Label(text=num, font_size="24sp", bold=True, color=TEXT_DARK, halign="center")
            n.bind(size=n.setter("text_size"))
            l = Label(text=lbl, font_size="11sp", color=TEXT_LIGHT, halign="center")
            l.bind(size=l.setter("text_size"))
            col.add_widget(n)
            col.add_widget(l)
            row.add_widget(col)
        stats_box.add_widget(row)
        root.add_widget(stats_box)

        root.add_widget(BoxLayout())

        # Buttons
        for text, color, callback in [
            ("Continue Learning", PRIMARY, self._on_continue),
            ("All Lessons", SECONDARY, self._on_select),
        ]:
            btn = Button(text=text, font_size="17sp", size_hint_y=None, height=dp(50),
                         background_normal="", background_down="",
                         background_color=(0, 0, 0, 0), color=BTN_TEXT)
            _c = color  # capture
            with btn.canvas.before:
                Color(*_c)
                _r = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(8)])
            btn.bind(pos=lambda i, *a, r=_r: setattr(r, "pos", i.pos),
                     size=lambda i, *a, r=_r: setattr(r, "size", i.size))
            btn.bind(on_release=callback)
            root.add_widget(btn)
            root.add_widget(BoxLayout(size_hint_y=None, height=dp(4)))

        root.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))
        self.add_widget(root)

    def _on_continue(self, *args):
        app = App.get_running_app()
        for unit in app.curriculum.get_units():
            if app.progress.get_lesson_status(unit["id"]) != "completed":
                self.manager.get_screen("exercise").unit_id = unit["id"]
                self.manager.current = "exercise"
                return
        self.manager.current = "lesson_select"

    def _on_select(self, *args):
        self.manager.current = "lesson_select"
