from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle

BG = (0.96, 0.94, 0.91, 1)
CARD = (0.99, 0.97, 0.95, 1)
PRIMARY = (0.62, 0.32, 0.20, 1)
SECONDARY = (0.40, 0.48, 0.32, 1)
CORRECT = (0.38, 0.48, 0.26, 1)
WARN = (0.68, 0.52, 0.24, 1)
ERROR = (0.70, 0.28, 0.22, 1)
TEXT_DARK = (0.15, 0.13, 0.11, 1)
TEXT_MID = (0.38, 0.34, 0.30, 1)
TEXT_LIGHT = (0.58, 0.54, 0.48, 1)
BTN_TEXT = (1.0, 0.98, 0.96, 1)


def _btn(text, color, height=dp(48)):
    btn = Button(text=text, font_size="17sp", size_hint_y=None, height=height,
                 background_normal="", background_down="",
                 background_color=(0, 0, 0, 0), color=BTN_TEXT)
    with btn.canvas.before:
        Color(*color)
        _r = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(8)])
    btn.bind(pos=lambda i, *a, r=_r: setattr(r, "pos", i.pos),
             size=lambda i, *a, r=_r: setattr(r, "size", i.size))
    return btn


class ResultsScreen(Screen):
    unit_id = ""
    score = 0
    total = 10

    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()

        root = BoxLayout(orientation="vertical", padding=dp(28), spacing=dp(12))
        with root.canvas.before:
            Color(*BG)
            _r = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, *a: setattr(_r, "pos", i.pos),
                  size=lambda i, *a: setattr(_r, "size", i.size))

        root.add_widget(BoxLayout(size_hint_y=0.1))

        root.add_widget(Label(text="Lesson Complete", font_size="24sp", bold=True,
                              color=TEXT_DARK, size_hint_y=None, height=dp(36)))

        pct = int((self.score / self.total) * 100) if self.total > 0 else 0
        sc = CORRECT if pct >= 70 else WARN if pct >= 50 else ERROR

        root.add_widget(Label(text=f"{self.score} / {self.total}", font_size="42sp",
                              bold=True, color=sc, size_hint_y=None, height=dp(60)))
        root.add_widget(Label(text=f"{pct}%", font_size="20sp", color=sc,
                              size_hint_y=None, height=dp(30)))

        # Words to review
        ws = app.progress.get_words_state()
        vocab = app.curriculum.get_vocab(self.unit_id)
        review = [f"{v['sl']}  →  {v['en']}" for v in vocab
                  if (s := ws.get(v["sl"])) and s.box == 1 and s.incorrect > 0]

        if review:
            root.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))
            root.add_widget(Label(text="Review these:", font_size="14sp", bold=True,
                                  color=TEXT_MID, size_hint_y=None, height=dp(22)))
            rtxt = Label(text="\n".join(review[:5]), font_size="14sp", color=TEXT_LIGHT,
                         size_hint_y=None, height=dp(len(review[:5]) * 22), halign="center")
            rtxt.bind(size=rtxt.setter("text_size"))
            root.add_widget(rtxt)

        root.add_widget(BoxLayout())

        retry = _btn("Retry", SECONDARY)
        retry.bind(on_release=self._retry)
        root.add_widget(retry)
        root.add_widget(BoxLayout(size_hint_y=None, height=dp(6)))

        cont = _btn("Continue", PRIMARY)
        cont.bind(on_release=self._continue)
        root.add_widget(cont)
        root.add_widget(BoxLayout(size_hint_y=None, height=dp(14)))

        self.add_widget(root)

    def _retry(self, *args):
        self.manager.get_screen("exercise").unit_id = self.unit_id
        self.manager.current = "exercise"

    def _continue(self, *args):
        self.manager.current = "lesson_select"
