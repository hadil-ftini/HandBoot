from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from Speech_Reco import listen_for_command
from object_detection import get_distance, capture_image
from enum import Enum

class BotState(Enum):
    IDLE = 'idle'
    LISTENING = 'listening'
    PROCESSING = 'processing'
    ERROR = 'error'

class StateManager:
    def __init__(self):
        self.current_state = BotState.IDLE
        self.observers = []

    def change_state(self, new_state):
        self.current_state = new_state
        self.notify_observers()

class VoiceBotGUI(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Add logo at the top
        self.logo = Image(
            source='voicebot_logo.png',
            size_hint=(1, 1.5),  # Make the logo slightly larger than other widgets
            allow_stretch=True,
            keep_ratio=True
        )
        
        self.label = Label(text="Bienvenue dans VoiceBot!")
        self.button = Button(text="Commencer")
        self.button.bind(on_press=self.start_voice_recognition)

        self.distance_button = Button(text="Mesurer la distance")
        self.distance_button.bind(on_press=self.measure_distance)

        self.exit_button = Button(
            text="Quitter",
            background_color=(1, 0, 0, 1),  # Red color
            size_hint=(1, 0.5)  # Make it shorter than other buttons
        )
        self.exit_button.bind(on_press=self.stop)

        self.progress = ProgressBar(max=100, value=0)

        # Add logo first, then other widgets
        self.layout.add_widget(self.logo)
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.button)
        self.layout.add_widget(self.distance_button)
        self.layout.add_widget(self.progress)
        self.layout.add_widget(self.exit_button)

        return self.layout

    def start_voice_recognition(self, instance):
        self.label.text = "Écoute en cours..."
        Clock.schedule_once(self.process_voice_command, 1)

    def process_voice_command(self, dt):
        command = listen_for_command()
        self.label.text = f"Vous avez dit : {command}"

    def measure_distance(self, instance):
        distance = get_distance()
        self.label.text = f"Distance: {distance} cm"
        if distance < 50:
            capture_image()

    def stop(self, instance):
        """Stop the application"""
        App.get_running_app().stop()

if __name__ == '__main__':
    VoiceBotGUI().run()