import speech_recognition as sr
from utils import speak
import logging

logger = logging.getLogger('VoiceBot')

# Define voice commands
COMMANDS = {
    'settings': ['paramètres', 'configuration', 'réglages'],
    'back': ['retour', 'précédent', 'arrière'],
    'logout': ['déconnexion', 'quitter', 'sortir'],
    'start': ['commencer', 'démarrer', 'lancer'],
    'stop': ['arrêter', 'stopper', 'fin'],
    'measure': ['mesurer', 'distance', 'capteur']
}

def get_command_type(text):
    """Convert recognized text to command type"""
    text = text.lower()
    for command_type, phrases in COMMANDS.items():
        if any(phrase in text for phrase in phrases):
            return command_type
    return None

def init_microphone():
    """Initialize and test microphone"""
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)
            return recognizer
    except Exception as e:
        logger.error(f"Error initializing microphone: {str(e)}")
        return None

def list_microphones():
    """List all available microphones"""
    try:
        from speech_recognition import Microphone
        mics = sr.Microphone.list_microphone_names()
        print("Available microphones:")
        for i, mic in enumerate(mics):
            print(f"{i}: {mic}")
        return mics
    except Exception as e:
        print(f"Error listing microphones: {str(e)}")
        return []

def listen_for_command(timeout=5):
    """Listen for voice command with improved handling"""
    try:
        recognizer = sr.Recognizer()
        
        with sr.Microphone() as source:
            print("Dites quelque chose...")
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = recognizer.listen(source, timeout=timeout)
            except sr.WaitTimeoutError:
                speak("Temps d'écoute dépassé")
                return "timeout"

            try:
                text = recognizer.recognize_google(audio, language="fr-FR")
                print(f"Vous avez dit : {text}")
                
                # Check if it's a known command
                command_type = get_command_type(text)
                if command_type:
                    speak(f"Commande reconnue : {text}")
                    return command_type
                else:
                    speak(f"Vous avez dit : {text}")
                    return text
                    
            except sr.UnknownValueError:
                speak("Je n'ai pas compris.")
                return "not_understood"
            except sr.RequestError:
                speak("Erreur du service vocal.")
                return "service_error"
                
    except Exception as e:
        error_msg = f"Erreur du microphone: {str(e)}"
        logger.error(error_msg)
        speak("Erreur du microphone")
        return "error"

def test_microphone():
    """Test microphone setup"""
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            return True
    except Exception as e:
        logger.error(f"Microphone test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Test microphone
    if test_microphone():
        print("Microphone test successful!")
        # Test voice recognition
        print("Testing voice recognition...")
        result = listen_for_command()
        print(f"Recognition result: {result}")
    else:
        print("Microphone test failed!")
