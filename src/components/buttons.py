from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation
from ..utils.colors import COLORS

class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.original_background = kwargs.get('background_color', COLORS['primary'])
        self.background_color = self.original_background
        
        with self.canvas.before:
            self.bg_color = Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(state=self._on_state)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        self.bg_color.rgba = self.background_color

    def _on_state(self, instance, value):
        if value == 'down':
            self.background_color = [c * 0.8 for c in self.original_background[:3]] + [self.original_background[3]]
        else:
            self.background_color = self.original_background
        self.bg_color.rgba = self.background_color

class VoiceInputButton(Button):
    def __init__(self, target_input, hint_text, **kwargs):
        super().__init__(**kwargs)
        self.target_input = target_input
        self.hint_text = hint_text
        self.background_normal = ''
        self.background_color = COLORS['accent']
        self.size_hint = (None, None)
        self.size = (40, 40)
        self.text = '🎤'
        self.font_size = '20sp'

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['button_normal']
        self.color = COLORS['text_light']
        self.border = (0, 0, 0, 0)
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def on_press(self):
        self.background_color = COLORS['button_down']
        Animation(background_color=COLORS['button_normal'], duration=0.3).start(self) 