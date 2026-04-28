from pathlib import Path

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

ASSETS_DIR = Path(__file__).parent.parent / "assets"

BG = (0.97, 0.95, 0.93, 1)
TEXT_DARK = (0.14, 0.12, 0.10, 1)
TEXT_LIGHT = (0.60, 0.56, 0.50, 1)
PRIMARY = (0.72, 0.30, 0.16, 1)


class SplashScreen(Screen):
    def on_enter(self):
        self.clear_widgets()

        root = FloatLayout()
        with root.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, *a: setattr(self._bg, "pos", i.pos),
                  size=lambda i, *a: setattr(self._bg, "size", i.size))

        # Labubu image
        splash_path = ASSETS_DIR / "splash_labubu.png"
        if splash_path.exists():
            img = Image(source=str(splash_path),
                        size_hint=(0.65, 0.65),
                        pos_hint={"center_x": 0.5, "center_y": 0.55})
            root.add_widget(img)

        # App name
        title = Label(text="Slovenčk",
                      font_size="36sp", bold=True, color=PRIMARY,
                      size_hint=(1, None), height=dp(50),
                      pos_hint={"center_x": 0.5, "y": 0.12})
        root.add_widget(title)

        # Subtitle
        sub = Label(text="Learn Slovenian",
                    font_size="15sp", color=TEXT_LIGHT,
                    size_hint=(1, None), height=dp(25),
                    pos_hint={"center_x": 0.5, "y": 0.08})
        root.add_widget(sub)

        # Tap to continue
        tap = Label(text="tap to start",
                    font_size="12sp", color=TEXT_LIGHT,
                    size_hint=(1, None), height=dp(20),
                    pos_hint={"center_x": 0.5, "y": 0.02})
        root.add_widget(tap)

        root.bind(on_touch_down=self._go)
        self.add_widget(root)

        # Auto-advance after 3 seconds
        self._auto = Clock.schedule_once(lambda dt: self._go(), 3)

    def _go(self, *args):
        if self._auto:
            self._auto.cancel()
            self._auto = None
        self.manager.current = "home"
