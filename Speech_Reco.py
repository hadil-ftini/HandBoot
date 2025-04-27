import speech_recognition as sr
from my_utils import speak
import logging
from language_support import language_manager
import time
import os

logger = logging.getLogger('VoiceBot')

# Enhanced voice commands
COMMANDS = {
    'fr': {
        'settings': ['paramètres', 'configuration', 'réglages'],
        'back': ['retour', 'précédent', 'arrière'],
        'logout': ['déconnexion', 'quitter', 'sortir'],
        'start': ['commencer', 'démarrer', 'lancer'],
        'stop': ['arrêter', 'stopper', 'fin'],
        'measure': ['mesurer', 'distance', 'capteur'],
        'language': ['langue', 'langage', 'changer langue'],
        'help': ['aide', 'assistance', 'guide'],
        'volume': ['volume', 'son', 'audio'],
        'camera': ['caméra', 'photo', 'image'],
        'go': ['avancer', 'aller', 'devant'],
        'backward': ['reculer', 'arrière'],
        'left': ['gauche'],
        'right': ['droite']
    },
    'en': {
        'settings': ['settings', 'configuration', 'setup'],
        'back': ['back', 'previous', 'return'],
        'logout': ['logout', 'quit', 'exit'],
        'start': ['start', 'begin', 'launch'],
        'stop': ['stop', 'end', 'finish'],
        'measure': ['measure', 'distance', 'sensor'],
        'language': ['language', 'change language', 'switch language'],
        'help': ['help', 'assistance', 'guide'],
        'volume': ['volume', 'sound', 'audio'],
        'camera': ['camera', 'photo', 'picture'],
        'go': ['go', 'forward', 'ahead'],
        'backward': ['backward', 'back', 'reverse'],
        'left': ['left'],
        'right': ['right']
    },
    'es': {
        'settings': ['configuración', 'ajustes', 'preferencias'],
        'back': ['atrás', 'volver', 'regresar'],
        'logout': ['salir', 'cerrar sesión', 'desconectar'],
        'start': ['comenzar', 'iniciar', 'empezar'],
        'stop': ['parar', 'detener', 'finalizar'],
        'measure': ['medir', 'distancia', 'sensor'],
        'language': ['idioma', 'cambiar idioma', 'lenguaje'],
        'help': ['ayuda', 'asistencia', 'guía'],
        'volume': ['volumen', 'sonido', 'audio'],
        'camera': ['cámara', 'foto', 'imagen'],
        'go': ['avanzar', 'adelante', 'ir'],
        'backward': ['retroceder', 'atrás'],
        'left': ['izquierda'],
        'right': ['derecha']
    }
}

def get_command_type(text, lang='fr'):
    """Convert recognized text to command type"""
    if lang not in COMMANDS:
        lang = 'fr'  # Default to French
        
    text = text.lower()
    for command_type, phrases in COMMANDS[lang].items():
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
            print("Adjusting for ambient noise...")
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Get current language before speaking
            current_lang = language_manager.get_current_language_code()
            print(f"Current language: {current_lang}")
            
            print("Listening...")
            speak(language_manager.get_text('speak_now'))
            
            try:
                # Listen for audio
                audio = recognizer.listen(source, timeout=timeout)
                
                # Map language codes to Google's speech recognition codes
                lang_map = {
                    'en': 'en-US',
                    'fr': 'fr-FR',
                    'es': 'es-ES',
                    'ar': 'ar-SA'
                }
                
                # Use mapped language code for recognition
                recognition_lang = lang_map.get(current_lang, 'en-US')
                print(f"Using recognition language: {recognition_lang}")
                
                # Recognize speech
                text = recognizer.recognize_google(audio, language=recognition_lang)
                print(f"Recognized: {text}")
                
                return text.lower()  # Always return lowercase for consistency
                    
            except sr.UnknownValueError:
                speak(language_manager.get_text('not_understood'))
                return "not_understood"
            except sr.RequestError as e:
                speak(language_manager.get_text('error'))
                return f"service_error: {str(e)}"
            except sr.WaitTimeoutError:
                speak(language_manager.get_text('timeout'))
                return "timeout"
                
    except Exception as e:
        error_msg = f"Microphone error: {str(e)}"
        logger.error(error_msg)
        speak(language_manager.get_text('error'))
        return f"error: {str(e)}"

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

def test_speech_recognition():
    """Test speech recognition with multiple languages"""
    print("\nTesting speech recognition...")
    
    # Test each supported language
    for lang_code in language_manager.SUPPORTED_LANGUAGES:
        language_manager.set_language(lang_code)
        lang_name = language_manager.SUPPORTED_LANGUAGES[lang_code]['name']
        
        print(f"\nTesting {lang_name}...")
        speak(language_manager.get_text('speak_now'))
        
        result = listen_for_command()
        print(f"Recognition result: {result}")
        
        time.sleep(2)  # Wait between languages

if __name__ == "__main__":
    # Test the speech recognition
    if test_microphone():
        print("Microphone test successful!")
        print("Testing voice recognition...")
        result = listen_for_command()
        print(f"Recognition result: {result}")
    else:
        print("Microphone test failed!")

# Switch to English
language_manager.set_language('en')

# Switch to French
language_manager.set_language('fr')