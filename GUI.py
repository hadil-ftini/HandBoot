from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from Speech_Reco import listen_for_command
from object_detection import get_distance, capture_image

class VoiceBotGUI(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        self.label = Label(text="Bienvenue dans VoiceBot!")
        self.button = Button(text="Commencer")
        self.button.bind(on_press=self.start_voice_recognition)

        self.distance_button = Button(text="Mesurer la distance")
        self.distance_button.bind(on_press=self.measure_distance)

        self.progress = ProgressBar(max=100, value=0)

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.button)
        self.layout.add_widget(self.distance_button)
        self.layout.add_widget(self.progress)

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
