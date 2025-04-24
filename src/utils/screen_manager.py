from kivy.uix.screenmanager import ScreenManager, SlideTransition

class AppScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()

    def switch_screen(self, screen_name, direction='left'):
        """Switch to a screen with specified direction"""
        print(f"Switching to {screen_name} screen")
        print(f"Available screens: {[screen.name for screen in self.screens]}")
        
        if screen_name not in [screen.name for screen in self.screens]:
            print(f"Error: Screen '{screen_name}' not found!")
            return False
            
        self.transition.direction = direction
        self.current = screen_name
        return True 