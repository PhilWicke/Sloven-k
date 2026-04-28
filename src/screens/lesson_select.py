from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse

# Warm but vibrant palette
BG = (0.97, 0.95, 0.93, 1)
CARD_BG = (1, 1, 1, 1)
CARD_DONE = (0.96, 0.98, 0.95, 1)
CARD_LOCKED = (0.96, 0.95, 0.94, 1)
PRIMARY = (0.72, 0.30, 0.16, 1)       # rich terracotta
SECONDARY = (0.36, 0.50, 0.32, 1)     # forest
TEXT_DARK = (0.14, 0.12, 0.10, 1)
TEXT_MID = (0.40, 0.36, 0.32, 1)
TEXT_LIGHT = (0.60, 0.56, 0.50, 1)
BTN_TEXT = (1, 1, 1, 1)

# Each unit gets a distinct warm color for its circle badge
UNIT_COLORS = {
    "pozdravi":  (0.72, 0.30, 0.16, 1),   # terracotta
    "stevila":   (0.55, 0.42, 0.22, 1),   # amber
    "barve":     (0.58, 0.28, 0.44, 1),   # plum
    "hrana":     (0.70, 0.48, 0.18, 1),   # golden
    "druzina":   (0.46, 0.36, 0.56, 1),   # lavender
    "zivali":    (0.36, 0.50, 0.32, 1),   # forest
    "telo":      (0.50, 0.38, 0.28, 1),   # sienna
    "oblacila":  (0.40, 0.46, 0.56, 1),   # slate blue
    "hisa":      (0.60, 0.44, 0.30, 1),   # clay
    "cas":       (0.34, 0.48, 0.46, 1),   # teal
}

UNIT_SYMBOLS = {
    "pozdravi":  "Hi",
    "stevila":   "#",
    "barve":     "\u25cf",   # ●
    "hrana":     "\u2663",   # ♣ (leaf-like)
    "druzina":   "\u2661",   # ♡
    "zivali":    "\u2618",   # ☘
    "telo":      "\u2606",   # ☆
    "oblacila":  "\u2302",   # ⌂
    "hisa":      "\u2302",   # ⌂
    "cas":       "\u25f4",   # ◴
}


class UnitBadge(BoxLayout):
    """Colored circle with a symbol inside."""
    def __init__(self, unit_id, locked=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))

        color = UNIT_COLORS.get(unit_id, PRIMARY)
        if locked:
            color = (0.78, 0.76, 0.73, 1)

        with self.canvas.before:
            Color(*color)
            self._circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

        sym = UNIT_SYMBOLS.get(unit_id, "?")
        lbl = Label(text=sym, font_size="16sp", bold=True, color=(1, 1, 1, 1),
                    halign="center", valign="middle")
        lbl.bind(size=lbl.setter("text_size"))
        self.add_widget(lbl)

    def _update(self, *a):
        self._circle.pos = self.pos
        self._circle.size = self.size


class LessonCard(BoxLayout):
    def __init__(self, unit, status, score, locked, on_tap, total, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(66)
        self.padding = [dp(12), dp(8), dp(12), dp(8)]
        self.spacing = dp(12)

        bg = CARD_LOCKED if locked else CARD_DONE if status == "completed" else CARD_BG
        with self.canvas.before:
            Color(0, 0, 0, 0.04)
            self._shadow = RoundedRectangle(pos=(self.x + 1, self.y - 1), size=self.size, radius=[dp(10)])
            Color(*bg)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Badge — use parent id for consistent color
        parent_id = unit.get("parent", unit["id"])
        self.add_widget(UnitBadge(parent_id, locked=locked, pos_hint={"center_y": 0.5}))

        # Text
        text_box = BoxLayout(orientation="vertical", spacing=dp(1))
        subunit_name = unit.get("subunit_name", unit["name_en"])
        subunit_num = unit.get("subunit", "")
        display = f"{subunit_num}. {subunit_name}" if subunit_num else unit["name_en"]
        name = Label(text=display,
                     font_size="15sp", bold=not locked,
                     color=TEXT_LIGHT if locked else TEXT_DARK,
                     halign="left", valign="center")
        name.bind(size=name.setter("text_size"))
        text_box.add_widget(name)

        status_str = "Locked" if locked else status.replace("_", " ").capitalize()
        if score > 0:
            status_str += f"  ·  {score}/{total}"
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

        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(8))
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
            Color(0.92, 0.90, 0.88, 1)
            _r = RoundedRectangle(pos=back.pos, size=back.size, radius=[dp(8)])
        back.bind(pos=lambda i, *a: setattr(_r, "pos", i.pos),
                  size=lambda i, *a: setattr(_r, "size", i.size))
        back.bind(on_release=lambda *a: setattr(self.manager, "current", "home"))
        header.add_widget(back)
        header.add_widget(Label(text="Lessons", font_size="22sp", bold=True, color=TEXT_DARK))
        root.add_widget(header)

        # List — group subunits under parent headers
        scroll = ScrollView()
        lst = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
        lst.bind(minimum_height=lst.setter("height"))

        prev_ok = True
        current_parent = None
        for unit in units:
            parent = unit.get("parent", unit["id"])
            # Show parent header when it changes
            if parent != current_parent:
                current_parent = parent
                header_lbl = Label(
                    text=f"{unit['name_sl']}  ·  {unit['name_en']}",
                    font_size="14sp", bold=True, color=TEXT_MID,
                    size_hint_y=None, height=dp(32),
                    halign="left", valign="bottom",
                    padding=(dp(8), 0),
                )
                header_lbl.bind(size=header_lbl.setter("text_size"))
                lst.add_widget(header_lbl)

            status = app.progress.get_lesson_status(unit["id"])
            score = app.progress.get_lesson_score(unit["id"])
            total = len(app.curriculum.get_vocab(unit["id"]))
            lst.add_widget(LessonCard(unit=unit, status=status, score=score,
                                      locked=not prev_ok, on_tap=self._start,
                                      total=total))
            prev_ok = (status == "completed") if prev_ok else False

        scroll.add_widget(lst)
        root.add_widget(scroll)
        self.add_widget(root)

    def _start(self, unit_id):
        self.manager.get_screen("exercise").unit_id = unit_id
        self.manager.current = "exercise"
