from kivy.core.window import Window
from GUI import VoiceBotGUI
from my_utils import tts
import logging

# Set window size before loading GUI
Window.size = (400, 300)

if __name__ == "__main__":
    try:
        # Test voices before starting the app
        print("Testing text-to-speech voices...")
        tts.test_voices()
    except Exception as e:
        print(f"Warning: Could not test voices - {str(e)}")
        logging.warning(f"Could not test voices: {str(e)}")
    
    # Start the application
    VoiceBotGUI().run()
