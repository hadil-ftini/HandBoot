from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from ..utils.colors import COLORS

class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = COLORS['secondary']
        self.foreground_color = COLORS['text']
        self.cursor_color = COLORS['primary']
        self.padding = [10, 10, 10, 10]
        self.multiline = False

class StyledSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['primary']
        self.color = COLORS['text_light']
        self.font_size = '16sp'
        self.option_cls = SpinnerOption
        
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[8,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class SpinnerOption(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['primary']
        self.color = COLORS['text_light']
        self.font_size = '14sp'
        
        with self.canvas.before:
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)

    def on_press(self):
        self.background_color = [c * 0.8 for c in COLORS['primary'][:3]] + [COLORS['primary'][3]] 