from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.settings import SettingsPanel
from kivy.core.window import Window
from kivy.uix.popup import Popup
from Speech_Reco import listen_for_command
from object_detection import get_distance, capture_image
from utils import verify_credentials, speak
from enum import Enum
import time
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch

# Set app theme colors
COLORS = {
    'primary': (0.2, 0.6, 0.9, 1),    # Blue
    'secondary': (0.95, 0.95, 0.95, 1), # Light Gray
    'accent': (0.2, 0.7, 0.3, 1),      # Green
    'warning': (0.9, 0.3, 0.1, 1),     # Red
}

class BotState(Enum):
    IDLE = 'idle'
    LISTENING = 'listening'
    PROCESSING = 'processing'
    ERROR = 'error'

class VoiceInputButton(Button):
    def __init__(self, target_input, hint_text, **kwargs):
        super().__init__(**kwargs)
        self.target_input = target_input
        self.hint_text = hint_text
        self.background_normal = ''
        self.background_color = COLORS['accent']
        self.size_hint = (None, None)
        self.size = (40, 40)
        self.text = '🎤'  # Microphone emoji
        self.font_size = '20sp'

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Add logo
        self.logo = Image(
            source='voicebot_logo.png',
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Login form
        form_layout = GridLayout(cols=3, spacing=10, size_hint_y=None, height=100)
        
        # Username row
        username_label = Label(text='Username:', color=COLORS['primary'])
        self.username_input = TextInput(multiline=False)
        self.username_voice_button = VoiceInputButton(
            self.username_input,
            "Dites votre nom d'utilisateur"
        )
        self.username_voice_button.bind(on_press=self.get_voice_username)
        
        # Password row
        password_label = Label(text='Password:', color=COLORS['primary'])
        self.password_input = TextInput(multiline=False, password=True)
        self.password_voice_button = VoiceInputButton(
            self.password_input,
            "Dites votre mot de passe"
        )
        self.password_voice_button.bind(on_press=self.get_voice_password)
        
        # Add all form elements
        form_layout.add_widget(username_label)
        form_layout.add_widget(self.username_input)
        form_layout.add_widget(self.username_voice_button)
        form_layout.add_widget(password_label)
        form_layout.add_widget(self.password_input)
        form_layout.add_widget(self.password_voice_button)
        
        # Login button
        self.login_button = CustomButton(
            text="Se connecter",
            background_color=COLORS['accent'],
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5}
        )
        self.login_button.bind(on_press=self.verify_credentials)
        
        # Error label
        self.error_label = Label(text="", color=COLORS['warning'])
        
        # Add widgets to layout
        layout.add_widget(self.logo)
        layout.add_widget(form_layout)
        layout.add_widget(self.error_label)
        layout.add_widget(self.login_button)
        
        self.add_widget(layout)

    def get_voice_username(self, instance):
        """Handle voice input for username"""
        speak("Dites votre nom d'utilisateur")
        Clock.schedule_once(lambda dt: self.process_voice_input(self.username_input), 0.5)

    def get_voice_password(self, instance):
        """Handle voice input for password"""
        speak("Dites votre mot de passe")
        Clock.schedule_once(lambda dt: self.process_voice_input(self.password_input), 0.5)

    def process_voice_input(self, target_input):
        """Process voice input and update the target input field"""
        try:
            text = listen_for_command()
            if text and text != "Commande non comprise" and text != "Erreur de reconnaissance":
                target_input.text = text.lower().strip()  # Convert to lowercase and remove spaces
                if target_input == self.password_input:
                    speak("Mot de passe enregistré")
                else:
                    speak(f"J'ai enregistré: {text}")
            else:
                speak("Je n'ai pas compris, veuillez réessayer")
        except Exception as e:
            speak("Une erreur s'est produite")
            self.error_label.text = str(e)

    def show_welcome_popup(self, username):
        """Show welcome popup and speak welcome message"""
        # Prepare welcome message
        message = f'Bienvenue, {username}!'
        
        # Create popup content
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        
        # Create and show popup
        popup = Popup(
            title='Connexion Réussie',
            content=content,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=True
        )
        
        # Schedule popup to close after 3 seconds
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)
        
        # Show popup
        popup.open()
        
        # Speak welcome message
        Clock.schedule_once(lambda dt: speak(message), 0.5)

    def verify_credentials(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        if verify_credentials(username, password):
            # Clear inputs first
            self.username_input.text = ""
            self.password_input.text = ""
            self.error_label.text = ""
            
            # Show welcome message
            self.show_welcome_popup(username)
            
            # Schedule transition to main screen
            Clock.schedule_once(lambda dt: self.switch_to_main(), 3)
        else:
            self.error_label.text = "Identifiants invalides!"
            speak("Identifiants invalides")

    def switch_to_main(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'main'

class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['primary']
        self.border = (2, 2, 2, 2)
        self.font_size = '18sp'
        self.size_hint_y = None
        self.height = 50

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Title
        title = Label(
            text="Paramètres",
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
        rate_label = Label(text="Vitesse:")
        self.rate_slider = Slider(min=100, max=200, value=150)
        self.rate_slider.bind(value=self.on_rate_change)
        rate_layout.add_widget(rate_label)
        rate_layout.add_widget(self.rate_slider)
        
        # Voice Feedback Switch
        feedback_layout = BoxLayout(size_hint_y=None, height=50)
        feedback_label = Label(text="Retour vocal:")
        self.feedback_switch = Switch(active=True)
        self.feedback_switch.bind(active=self.on_feedback_change)
        feedback_layout.add_widget(feedback_label)
        feedback_layout.add_widget(self.feedback_switch)
        
        # Back Button
        back_button = CustomButton(
            text="Retour",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5}
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
        # Update TTS volume
        from utils import tts
        tts.engine.setProperty('volume', value)

    def on_rate_change(self, instance, value):
        # Update TTS rate
        from utils import tts
        tts.engine.setProperty('rate', value)

    def on_feedback_change(self, instance, value):
        # Enable/disable voice feedback
        from utils import config_manager
        config_manager._config['app']['voice_feedback'] = value

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state_manager = StateManager()
        self.build_ui()

    def build_ui(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Add logo
        self.logo = Image(
            source='voicebot_logo.png',
            size_hint=(1, 1.2),
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Status layout
        status_layout = BoxLayout(size_hint_y=None, height=40)
        self.status_label = Label(
            text="État: Prêt",
            color=COLORS['primary']
        )
        status_layout.add_widget(self.status_label)
        
        # Buttons layout
        buttons_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=120)
        
        # Create buttons
        self.start_button = CustomButton(
            text="Commencer",
            background_color=COLORS['accent']
        )
        self.start_button.bind(on_press=self.start_voice_recognition)
        
        self.distance_button = CustomButton(
            text="Mesurer Distance",
            background_color=COLORS['primary']
        )
        self.distance_button.bind(on_press=self.measure_distance)

        self.settings_button = CustomButton(
            text="Paramètres",
            background_color=COLORS['primary']
        )
        
        self.logout_button = CustomButton(
            text="Déconnexion",
            background_color=COLORS['warning']
        )
        self.logout_button.bind(on_press=self.logout)
        
        # Modify settings button binding
        self.settings_button.bind(on_press=self.show_settings)
        
        # Add buttons to layout
        buttons_layout.add_widget(self.start_button)
        buttons_layout.add_widget(self.distance_button)
        buttons_layout.add_widget(self.settings_button)
        buttons_layout.add_widget(self.logout_button)
        
        # Progress bar
        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=30
        )
        
        # Add all elements to main layout
        main_layout.add_widget(self.logo)
        main_layout.add_widget(status_layout)
        main_layout.add_widget(buttons_layout)
        main_layout.add_widget(self.progress)
        
        # Add the main layout to the screen
        self.add_widget(main_layout)
        
        # Initialize state manager
        self.state_manager.add_observer(self)

    def on_state_change(self, new_state):
        """Handle state changes"""
        state_messages = {
            BotState.IDLE: "État: Prêt",
            BotState.LISTENING: "État: Écoute en cours...",
            BotState.PROCESSING: "État: Traitement...",
            BotState.ERROR: "État: Erreur"
        }
        self.status_label.text = state_messages.get(new_state, "État: Inconnu")
        speak(self.status_label.text)  # Announce state changes

    def start_voice_recognition(self, instance):
        self.state_manager.change_state(BotState.LISTENING)
        Clock.schedule_once(self.process_voice_command, 1)

    def process_voice_command(self, dt):
        self.state_manager.change_state(BotState.PROCESSING)
        command = listen_for_command()
        self.status_label.text = f"Commande: {command}"
        self.state_manager.change_state(BotState.IDLE)

    def measure_distance(self, instance):
        self.state_manager.change_state(BotState.PROCESSING)
        distance = get_distance()
        self.status_label.text = f"Distance mesurée: {distance} cm"
        speak(f"Distance mesurée: {distance} centimètres")
        if distance < 50:
            capture_image()
        self.state_manager.change_state(BotState.IDLE)

    def logout(self, instance):
        speak("Au revoir!")
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'login'

    def show_settings(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'settings'

class StateManager:
    def __init__(self):
        self.current_state = BotState.IDLE
        self.observers = []
        
    def change_state(self, new_state):
        self.current_state = new_state
        self.notify_observers()
        
    def add_observer(self, observer):
        self.observers.append(observer)
        
    def notify_observers(self):
        for observer in self.observers:
            observer.on_state_change(self.current_state)

class VoiceBotGUI(App):
    def build(self):
        # Set window size and title
        Window.size = (400, 600)
        self.title = 'VoiceBot Assistant'
        
        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        return sm

if __name__ == '__main__':
    VoiceBotGUI().run()