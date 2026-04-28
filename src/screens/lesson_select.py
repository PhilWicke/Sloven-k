from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle

BG = (0.96, 0.94, 0.91, 1)
CARD = (0.99, 0.97, 0.95, 1)
CARD_DONE = (0.94, 0.96, 0.92, 1)
CARD_LOCKED = (0.94, 0.92, 0.90, 1)
PRIMARY = (0.66, 0.36, 0.24, 1)       # darker terracotta for contrast
SECONDARY = (0.45, 0.53, 0.38, 1)     # darker sage
ACCENT = (0.58, 0.46, 0.36, 1)
TEXT_DARK = (0.18, 0.16, 0.14, 1)
TEXT_MID = (0.42, 0.38, 0.34, 1)
TEXT_LIGHT = (0.62, 0.58, 0.52, 1)
BTN_TEXT = (0.99, 0.97, 0.95, 1)

UNIT_SYMBOLS = {
    "pozdravi": "Hi",
    "stevila": "12",
    "barve": "Co",       # colors
    "hrana": "Fd",        # food
    "druzina": "Fm",      # family
    "zivali": "An",       # animals
    "telo": "Bd",         # body
    "oblacila": "Cl",     # clothing
    "hisa": "Ho",         # house
    "cas": "Ti",          # time
}


class LessonCard(BoxLayout):
    def __init__(self, unit, status, score, locked, on_tap, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(68)
        self.padding = [dp(10), dp(6), dp(10), dp(6)]
        self.spacing = dp(12)

        bg_color = CARD_LOCKED if locked else CARD_DONE if status == "completed" else CARD
        with self.canvas.before:
            Color(0, 0, 0, 0.025)
            self._shadow = RoundedRectangle(pos=(self.x + 1, self.y - 1), size=self.size, radius=[dp(8)])
            Color(*bg_color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Symbol badge instead of image
        symbol = UNIT_SYMBOLS.get(unit["id"], "??")
        badge = BoxLayout(size_hint=(None, None), width=dp(42), height=dp(42),
                          pos_hint={"center_y": 0.5})
        badge_color = TEXT_LIGHT if locked else ACCENT
        with badge.canvas.before:
            Color(*badge_color)
            self._badge_bg = RoundedRectangle(pos=badge.pos, size=badge.size, radius=[dp(6)])
        badge.bind(pos=lambda i, *a: setattr(self._badge_bg, "pos", i.pos),
                   size=lambda i, *a: setattr(self._badge_bg, "size", i.size))
        sym_label = Label(text=symbol, font_size="16sp", bold=True,
                          color=BTN_TEXT, halign="center", valign="middle")
        sym_label.bind(size=sym_label.setter("text_size"))
        badge.add_widget(sym_label)
        self.add_widget(badge)

        # Text
        text_box = BoxLayout(orientation="vertical", spacing=dp(2))
        name = Label(text=f"{unit['name_sl']}  ·  {unit['name_en']}",
                     font_size="15sp", bold=not locked,
                     color=TEXT_LIGHT if locked else TEXT_DARK,
                     halign="left", valign="center")
        name.bind(size=name.setter("text_size"))
        text_box.add_widget(name)

        status_str = "Locked" if locked else status.replace("_", " ").capitalize()
        if score > 0:
            status_str += f"  ·  {score}/20"
        sub = Label(text=status_str, font_size="11sp", color=TEXT_LIGHT,
                    halign="left", valign="center")
        sub.bind(size=sub.setter("text_size"))
        text_box.add_widget(sub)
        self.add_widget(text_box)

        if not locked:
            label = "Begin" if status == "not_started" else "Resume" if status == "in_progress" else "Review"
            btn_color = PRIMARY if status != "completed" else SECONDARY
            btn = Button(text=label, font_size="12sp",
                         size_hint=(None, None), width=dp(58), height=dp(30),
                         pos_hint={"center_y": 0.5},
                         background_normal="", background_down="",
                         background_color=(0, 0, 0, 0), color=BTN_TEXT)
            with btn.canvas.before:
                Color(*btn_color)
                _r = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(6)])
            btn.bind(pos=lambda i, *a, r=_r: setattr(r, "pos", i.pos),
                     size=lambda i, *a, r=_r: setattr(r, "size", i.size))
            btn.bind(on_release=lambda *a: on_tap(unit["id"]))
            self.add_widget(btn)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._shadow.pos = (self.x + 1, self.y - 1)
        self._shadow.size = self.size


class LessonSelectScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        units = app.curriculum.get_units()

        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        with root.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, *a: setattr(self._bg, "pos", i.pos),
                  size=lambda i, *a: setattr(self._bg, "size", i.size))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        back = Button(text="<", size_hint=(None, None), width=dp(36), height=dp(36),
                      font_size="18sp", background_normal="", background_down="",
                      background_color=(0, 0, 0, 0), color=TEXT_MID)
        with back.canvas.before:
            Color(0.90, 0.88, 0.85, 1)
            _r = RoundedRectangle(pos=back.pos, size=back.size, radius=[dp(6)])
        back.bind(pos=lambda i, *a: setattr(_r, "pos", i.pos),
                  size=lambda i, *a: setattr(_r, "size", i.size))
        back.bind(on_release=lambda *a: setattr(self.manager, "current", "home"))
        header.add_widget(back)
        header.add_widget(Label(text="Lessons", font_size="22sp", bold=True, color=TEXT_DARK))
        root.add_widget(header)

        # List
        scroll = ScrollView()
        lst = BoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None)
        lst.bind(minimum_height=lst.setter("height"))

        prev_ok = True
        for unit in units:
            status = app.progress.get_lesson_status(unit["id"])
            score = app.progress.get_lesson_score(unit["id"])
            lst.add_widget(LessonCard(unit=unit, status=status, score=score,
                                      locked=not prev_ok, on_tap=self._start))
            prev_ok = (status == "completed") if prev_ok else False

        scroll.add_widget(lst)
        root.add_widget(scroll)
        self.add_widget(root)

    def _start(self, unit_id):
        self.manager.get_screen("exercise").unit_id = unit_id
        self.manager.current = "exercise"
