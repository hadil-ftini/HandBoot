from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition


from ..components.custom_buttons import CustomButton
from ..components.state_manager import StateManager, BotState
from ..utils.colors import COLORS
from my_utils import speak
from Speech_Reco import listen_for_command
from src.utils.screen_manager import AppScreenManager

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
            background_color=COLORS['accent'],
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.start_button.bind(on_press=self.start_voice_recognition)
        
        self.object_button = CustomButton(
            text="Object Identification",
            background_color=COLORS['primary'],
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.object_button.bind(on_press=self.open_object_identification)

        self.settings_button = CustomButton(
            text="Settings",
            background_color=COLORS['secondary'],
            color=COLORS['text'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.settings_button.bind(on_press=self.show_settings)
        
        self.logout_button = CustomButton(
            text="Logout",
            background_color=COLORS['warning'],
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.logout_button.bind(on_press=self.logout)
        
        # Add buttons to layout
        buttons_layout.add_widget(self.start_button)
        buttons_layout.add_widget(self.object_button)
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
        speak(self.status_label.text)

    def start_voice_recognition(self, instance):
        """Start voice recognition process"""
        self.state_manager.change_state(BotState.LISTENING)
        Clock.schedule_once(self.process_voice_command, 1)

    def process_voice_command(self, dt):
        """Process voice command"""
        self.state_manager.change_state(BotState.PROCESSING)
        command = listen_for_command()
        self.status_label.text = f"Command: {command}"
        self.state_manager.change_state(BotState.IDLE)

    def open_object_identification(self, instance):
        """Open object identification screen"""
        try:
            print("Opening object identification screen...")
            self.manager.transition.direction = 'left'
            self.manager.current = 'object_identification'
        except Exception as e:
            print(f"Error switching to object identification: {e}")

    def show_settings(self, instance):
        """Open settings screen"""
        try:
            print("Opening settings screen...")
            self.manager.transition.direction = 'left'
            self.manager.current = 'settings'
        except Exception as e:
            print(f"Error switching to settings: {e}")

    def logout(self, instance):
        """Handle logout"""
        speak("Goodbye!")
        self.manager.transition.direction = 'right'
        self.manager.current = 'login'

    def on_enter(self):
        """Called when screen is entered"""
        self.state_manager.change_state(BotState.IDLE) 