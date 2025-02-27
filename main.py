from kivy.core.window import Window
from GUI import VoiceBotGUI

# Set window size before loading GUI
Window.size = (400, 300)

if __name__ == "__main__":
    VoiceBotGUI().run()
