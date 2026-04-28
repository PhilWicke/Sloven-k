import os
import sys
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).parent))

# Set window size before Kivy init (desktop testing)
os.environ.setdefault("KIVY_WINDOW", "sdl2")
from kivy.config import Config
Config.set("graphics", "width", "360")
Config.set("graphics", "height", "640")
Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from screens.home import HomeScreen
from screens.lesson_select import LessonSelectScreen
from screens.exercise import ExerciseScreen
from screens.results import ResultsScreen
from services.curriculum import CurriculumLoader
from services.progress import ProgressManager

# Load theme
theme_path = Path(__file__).parent / "theme" / "style.kv"
if theme_path.exists():
    Builder.load_file(str(theme_path))


class SlovencekApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.curriculum = CurriculumLoader()
        self.progress = ProgressManager()

    def build(self):
        self.title = "Slovenčk"
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(LessonSelectScreen(name="lesson_select"))
        sm.add_widget(ExerciseScreen(name="exercise"))
        sm.add_widget(ResultsScreen(name="results"))
        return sm


if __name__ == "__main__":
    SlovencekApp().run()
