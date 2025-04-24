from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from my_utils import config_manager
from language_support import language_manager

# Import screens
from src.screens.login_screen import LoginScreen
from src.screens.main_screen import MainScreen
from src.screens.settings_screen import SettingsScreen
from src.screens.object_identification_screen import ObjectIdentificationScreen

class VoiceBotGUI(App):
    def build(self):
        try:
            # Set window size and title
            Window.size = (400, 600)
            self.title = 'VoiceBot Assistant'
            
            # Create screen manager with transition
            self.sm = ScreenManager(transition=SlideTransition())
            from my_utils import config_manager
            from language_support import language_manager
        
            saved_lang = config_manager.get('app.language', 'en')
            language_manager.set_language(saved_lang)
            # Create and add all screens
            screens = [
                LoginScreen(name='login'),
                MainScreen(name='main'),
                SettingsScreen(name='settings'),
                ObjectIdentificationScreen(name='object_identification')
            ]
            
            # Add screens to manager
            for screen in screens:
                print(f"Adding screen: {screen.name}")
                self.sm.add_widget(screen)
            
            # Set initial screen
            self.sm.current = 'login'
            
            return self.sm
            
        except Exception as e:
            print(f"Error in build: {e}")
            raise

if __name__ == '__main__':
    VoiceBotGUI().run()