from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from ..utils.colors import COLORS

class StyledLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = COLORS['text']
        self.padding = [10, 10]
        with self.canvas.before:
            Color(*COLORS['secondary'])
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[5,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size 