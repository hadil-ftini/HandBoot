from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup

from ..components.custom_buttons import VoiceInputButton, CustomButton
from ..components.custom_inputs import StyledTextInput, StyledSpinner
from ..utils.colors import COLORS
from my_utils import verify_credentials, speak
from Speech_Reco import listen_for_command

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
        self.username_input = StyledTextInput(multiline=False)
        self.username_voice_button = VoiceInputButton(
            self.username_input,
            "Dites votre nom d'utilisateur"
        )
        self.username_voice_button.bind(on_press=self.get_voice_username)
        
        # Password row
        password_label = Label(text='Password:', color=COLORS['primary'])
        self.password_input = StyledTextInput(multiline=False, password=True)
        self.password_voice_button = VoiceInputButton(
            self.password_input,
            "Dites votre mot de passe"
        )
        self.password_voice_button.bind(on_press=self.get_voice_password)
        
        # Add form elements
        form_layout.add_widget(username_label)
        form_layout.add_widget(self.username_input)
        form_layout.add_widget(self.username_voice_button)
        form_layout.add_widget(password_label)
        form_layout.add_widget(self.password_input)
        form_layout.add_widget(self.password_voice_button)
        
        # Language selector
        language_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=10,
            padding=[0, 10, 0, 10]
        )
        
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
        
        # Add all widgets to main layout
        layout.add_widget(self.logo)
        layout.add_widget(form_layout)
        layout.add_widget(self.error_label)
        layout.add_widget(language_layout)  # Add language layout directly
        layout.add_widget(self.login_button)
        
        self.add_widget(layout)

    def get_voice_username(self, instance):
        speak("Say YOUR name")
        Clock.schedule_once(lambda dt: self.process_voice_input(self.username_input), 0.5)

    def get_voice_password(self, instance):
        speak("say your password")
        Clock.schedule_once(lambda dt: self.process_voice_input(self.password_input), 0.5)

    def process_voice_input(self, target_input):
        try:
            text = listen_for_command()
            if text and text != "Commande non comprise" and text != "Erreur de reconnaissance":
                target_input.text = text.lower().strip()
                if target_input == self.password_input:
                    speak("Saved password")
                else:
                    speak(f"I recorded: {text}")
            else:
                speak("I didn't understand, please try again.")
        except Exception as e:
            speak("An error has occurred")
            self.error_label.text = str(e)

    def verify_credentials(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        if verify_credentials(username, password):
            self.username_input.text = ""
            self.password_input.text = ""
            self.error_label.text = ""
            self.show_welcome_popup(username)
            Clock.schedule_once(lambda dt: self.switch_to_main(), 3)
        else:
            self.error_label.text = "Invalid login!"
            speak("Invalid login!")

    def show_welcome_popup(self, username):
        message = f'Welcome, {username}!'
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        popup = Popup(
            title='Connection Successful',
            content=content,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=True
        )
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)
        popup.open()
        Clock.schedule_once(lambda dt: speak(message), 0.5)

    def switch_to_main(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'main'

    def on_language_select(self, spinner, text):
        from language_support import language_manager
        from my_utils import config_manager
        
        lang_map = {
            'Français': 'fr',
            'English': 'en',
            'Español': 'es',
            'العربية': 'ar'
        }
        
        lang_code = lang_map.get(text, 'fr')
        language_manager.set_language(lang_code)
        
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
 