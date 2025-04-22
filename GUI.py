from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.settings import SettingsPanel
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.animation import Animation
from Speech_Reco import listen_for_command
from my_utils import verify_credentials, speak, tts
from enum import Enum
import time
from object_detection import detect_objects

from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget

# Enhanced color scheme
COLORS = {
    'primary': (0.2, 0.6, 0.9, 1),      # Blue
    'secondary': (0.95, 0.95, 0.95, 1),  # Light Gray
    'accent': (0.2, 0.7, 0.3, 1),        # Green
    'warning': (0.9, 0.3, 0.1, 1),       # Red
    'background': (1, 1, 1, 1),          # White
    'text': (0.1, 0.1, 0.1, 1),          # Dark Gray
    'text_light': (1, 1, 1, 1)           # White
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
        self.hint_text = hint_text #indice
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
        
        # Language selector layout
        language_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=10,
            padding=[0, 10, 0, 10]  # Add some vertical padding
        )
        
        # Create language spinner (dropdown)
        self.language_spinner = StyledSpinner(
            text='English',
            values=('English', 'Français', 'Español', 'العربية'),
            size_hint=(None, None),
            size=(150, 40),
            pos_hint={'center_x': 0.5}
        )
        self.language_spinner.bind(text=self.on_language_select)
        
        # Center the language spinner
        language_layout.add_widget(Widget())  # Left spacer
        language_layout.add_widget(self.language_spinner)
        language_layout.add_widget(Widget())  # Right spacer
        
        # Error label
        self.error_label = Label(text="", color=COLORS['warning'])
        
        # Login button
        self.login_button = CustomButton(
            text="Se connecter",
            background_color=COLORS['accent'],
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5}
        )
        self.login_button.bind(on_press=self.verify_credentials)
        
        # Add widgets to layout in new order
        layout.add_widget(self.logo)
        layout.add_widget(form_layout)
        layout.add_widget(self.error_label)
        layout.add_widget(language_layout)  # Add language selector before login button
        layout.add_widget(self.login_button)
        
        self.add_widget(layout)

    def get_voice_username(self, instance):
        """Handle voice input for username"""
        speak(" Say YOUR name ")
        Clock.schedule_once(lambda dt: self.process_voice_input(self.username_input), 0.5)

    def get_voice_password(self, instance):
        """Handle voice input for password"""
        speak("say your password")
        Clock.schedule_once(lambda dt: self.process_voice_input(self.password_input), 0.5)

    def process_voice_input(self, target_input):
        """Process voice input and update the target input field"""
        try:
            text = listen_for_command()
            if text and text != "Commande non comprise" and text != "Erreur de reconnaissance":
                target_input.text = text.lower().strip()  # Convert to lowercase and remove spaces
                if target_input == self.password_input:
                    speak("Saved password")
                else:
                    speak(f"I recorded: {text}")
            else:
                speak("I didn't understand, please try again.")
        except Exception as e:
            speak("An error has occurred")
            self.error_label.text = str(e)

    def show_welcome_popup(self, username):
        """Show welcome popup and speak welcome message"""
        # Prepare welcome message
        message = f'Welcome, {username}!'
        
        # Create popup content
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        
        # Create and show popup
        popup = Popup(
            title='Connection Successful',
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
            self.error_label.text = "Invalid login!"
            speak("Invalid login !")

    def switch_to_main(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'main'

    def on_language_select(self, spinner, text):
        """Handle language selection"""
        from language_support import language_manager
        from my_utils import config_manager, speak
        
        # Map display text to language codes
        lang_map = {
            'Français': 'fr',
            'English': 'en',
            'Español': 'es',
            'العربية': 'ar'
        }
        
        lang_code = lang_map.get(text, 'fr')
        
        # Set the language
        language_manager.set_language(lang_code)
        
        # Save the language preference
        if 'app' not in config_manager._config:
            config_manager._config['app'] = {}
        config_manager._config['app']['language'] = lang_code
        config_manager.load_config()
        
        # Update UI text based on selected language
        welcome_messages = {
            'fr': 'Bienvenue',
            'en': 'Welcome',
            'es': 'Bienvenido',
            'ar': 'مرحبا'
        }
        
        # Update button and label text
        self.login_button.text = {
            'fr': 'Se connecter',
            'en': 'Login',
            'es': 'Iniciar sesión',
            'ar': 'تسجيل الدخول'
        }.get(lang_code, 'Login')
        
        # Speak welcome message
        speak(welcome_messages.get(lang_code, welcome_messages['en']))

class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        # Store the original background color
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
        # Update the background color
        self.bg_color.rgba = self.background_color

    def _on_state(self, instance, value):
        if value == 'down':
            # Darken the button when pressed
            self.background_color = [
                c * 0.8 for c in self.original_background[:3]
            ] + [self.original_background[3]]
        else:
            # Restore original color when released
            self.background_color = self.original_background
        # Update the canvas color
        self.bg_color.rgba = self.background_color

    def on_background_color(self, instance, value):
        """Called when background_color property changes"""
        if hasattr(self, 'bg_color'):
            self.bg_color.rgba = value

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Title
        title = Label(
            text="Setting",
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
            text="Back",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            color=(1, 1, 1, 1),  # White text
            background_color=(0.2, 0.2, 0.2, 1)  # Dark gray background
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
        tts.engine.setProperty('volume', value)

    def on_rate_change(self, instance, value):
        # Update TTS rate
        tts.engine.setProperty('rate', value)

    def on_feedback_change(self, instance, value):
        # Enable/disable voice feedback
        from my_utils import config_manager
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
            text="Status: Ready",
            color=(0, 0.8, 0.8, 1)
        )
        status_layout.add_widget(self.status_label)
        
        # Buttons layout
        buttons_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=120)
        
        # Create buttons
        self.start_button = CustomButton(
            text="Start",
            background_color=COLORS['accent'],  # Green color
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.start_button.bind(on_press=self.start_voice_recognition)
        
        self.distance_button = CustomButton(
            text="Object Identification",
            background_color=COLORS['primary'],  # Blue color
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.distance_button.bind(on_press=self.measure_distance)

        self.settings_button = CustomButton(
            text="Settings",
            background_color=COLORS['secondary'],  # Light gray color
            color=COLORS['text'],
            size_hint=(None, None),
            size=(200, 50)
        )
        
        self.logout_button = CustomButton(
            text="Logout",
            background_color=COLORS['warning'],  # Red color
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
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
            BotState.IDLE: "Status: Ready",
            BotState.LISTENING: "Status: Listening...",
            BotState.PROCESSING: "Status: Processing...",
            BotState.ERROR: "Status: Error"
        }
        self.status_label.text = state_messages.get(new_state, "Status: Unknown")
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
        detect_objects()

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
        self.font_size = '16sp'  # Slightly larger font
        self.option_cls = SpinnerOption
        
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[8,]  # Slightly larger radius
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

# Add this new class for styled dropdown options
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
        self.background_color = [
            c * 0.8 for c in COLORS['primary'][:3]
        ] + [COLORS['primary'][3]]

class VoiceBotGUI(App):
    def build(self):
        # Set window size and title
        Window.size = (400, 600)
        self.title = 'VoiceBot Assistant'
        
        # Create screen manager
        sm = ScreenManager()
        
        # Load saved language from config
        from my_utils import config_manager
        from language_support import language_manager
        
        saved_lang = config_manager.get('app.language', 'en')
        language_manager.set_language(saved_lang)
        
        # Add screens
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        return sm

if __name__ == '__main__':
    VoiceBotGUI().run()

print("Available voices:")
for voice in tts.get_available_voices():
    print(f"Name: {voice['name']}")