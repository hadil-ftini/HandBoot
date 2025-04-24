from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.clock import Clock

from ..components.custom_buttons import CustomButton
from ..utils.colors import COLORS
from my_utils import tts, config_manager

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Title
        title = Label(
            text="Settings",
            font_size='24sp',
            size_hint_y=None,
            height=50
        )
        
        # Volume Control
        volume_layout = BoxLayout(size_hint_y=None, height=50)
        volume_label = Label(text="Volume:")
        self.volume_slider = Slider(min=0, max=1, value=0.8)
        self.volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(volume_label)
        volume_layout.add_widget(self.volume_slider)
        
        # Speech Rate Control
        rate_layout = BoxLayout(size_hint_y=None, height=50)
        rate_label = Label(text="Speed:")
        self.rate_slider = Slider(min=100, max=200, value=150)
        self.rate_slider.bind(value=self.on_rate_change)
        rate_layout.add_widget(rate_label)
        rate_layout.add_widget(self.rate_slider)
        
        # Voice Feedback Switch
        feedback_layout = BoxLayout(size_hint_y=None, height=50)
        feedback_label = Label(text="Voice Feedback:")
        self.feedback_switch = Switch(active=True)
        self.feedback_switch.bind(active=self.on_feedback_change)
        feedback_layout.add_widget(feedback_label)
        feedback_layout.add_widget(self.feedback_switch)
        
        # Back Button
        back_button = CustomButton(
            text="Back",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            color=(1, 1, 1, 1),
            background_color=(0.2, 0.2, 0.2, 1)
        )
        back_button.bind(on_press=self.go_back)
        
        # Add all widgets
        layout.add_widget(title)
        layout.add_widget(volume_layout)
        layout.add_widget(rate_layout)
        layout.add_widget(feedback_layout)
        layout.add_widget(back_button)
        
        self.add_widget(layout)

    def on_volume_change(self, instance, value):
        tts.engine.setProperty('volume', value)

    def on_rate_change(self, instance, value):
        tts.engine.setProperty('rate', value)

    def on_feedback_change(self, instance, value):
        config_manager._config['app']['voice_feedback'] = value

    def go_back(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'main'

    def on_pre_enter(self):
        """Called before entering the screen"""
        print("About to enter settings screen")

    def on_enter(self):
        """Called when entering the screen"""
        print("Entered settings screen")

    def on_pre_leave(self):
        """Called before leaving the screen"""
        print("About to leave settings screen")

    def on_leave(self):
        """Called when leaving the screen"""
        print("Left settings screen") 