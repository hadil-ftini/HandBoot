import pyttsx3
import logging
import yaml
import os
import cv2
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

# Initialize logging
logging.basicConfig(
    filename='voicebot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('VoiceBot')

class ConfigManager:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self.load_config()

    def load_config(self, config_file: str = 'config.yaml') -> None:
        """Load configuration from YAML file"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as file:
                    self._config = yaml.safe_load(file)
                logger.info("Configuration loaded successfully")
            else:
                self._config = self.get_default_config()
                logger.warning("Using default configuration")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self._config = self.get_default_config()

    def get_default_config(self) -> dict:
        """Return default configuration"""
        return {
            'app': {
                'language': 'fr-FR',
                'voice_rate': 150,
                'voice_volume': 1.0
            },
            'camera': {
                'capture_dir': 'captures'
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        try:
            value = self._config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

class TextToSpeech:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.engine = None
        self.current_language = 'fr'
        self.initialize_engine()

    def initialize_engine(self):
        """Initialize TTS engine with SAPI5 for Windows"""
        try:
            if os.name == 'nt':  # Windows
                self.engine = pyttsx3.init(driverName='sapi5')
            else:
                self.engine = pyttsx3.init()
            
            if self.engine:
                self.configure_engine()
                logger.info("TTS engine initialized successfully")
            else:
                logger.error("Failed to initialize TTS engine")
        except Exception as e:
            logger.error(f"Error initializing TTS: {str(e)}")
            self.engine = None

    def configure_engine(self):
        """Configure TTS engine with optimal settings"""
        if not self.engine:
            return

        try:
            # Get all available voices
            voices = self.engine.getProperty('voices')
            
            # Dictionary to store best voices for each language
            self.voice_map = {
                'fr': None,
                'en': None,
                'es': None
            }

            # Find the best voice for each language
            for voice in voices:
                if "french" in voice.name.lower():
                    self.voice_map['fr'] = voice.id
                elif "english" in voice.name.lower():
                    self.voice_map['en'] = voice.id
                elif "spanish" in voice.name.lower():
                    self.voice_map['es'] = voice.id

            # Set default voice (French)
            if self.voice_map['fr']:
                self.engine.setProperty('voice', self.voice_map['fr'])
            
            # Set default properties
            self.engine.setProperty('rate', 150)    # Normal speed
            self.engine.setProperty('volume', 1.0)  # Maximum volume
            
            logger.info("TTS engine configured successfully")
            
        except Exception as e:
            logger.error(f"Error configuring TTS: {str(e)}")

    def speak(self, text: str) -> None:
        """Speak text with appropriate voice and settings"""
        if not text or not self.engine:
            return

        try:
            # Get current language from language manager
            from language_support import language_manager
            current_lang = language_manager.get_current_language_code()

            # Set voice and properties based on language
            if current_lang in self.voice_map and self.voice_map[current_lang]:
                self.engine.setProperty('voice', self.voice_map[current_lang])
                
                # Adjust rate based on language
                if current_lang == 'en':
                    self.engine.setProperty('rate', 130)
                elif current_lang == 'es':
                    self.engine.setProperty('rate', 140)
                else:
                    self.engine.setProperty('rate', 150)

            # Speak the text
            self.engine.say(text)
            self.engine.runAndWait()
            logger.info(f"TTS success: {text}")

        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            # Fallback: Just print the text
            print(f"Speech (fallback): {text}")

    def get_available_voices(self):
        """List all available voices"""
        if not self.engine:
            return []
        
        voices = []
        try:
            for voice in self.engine.getProperty('voices'):
                voices.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages if hasattr(voice, 'languages') else []
                })
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
        
        return voices

class ImageHandler:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.capture_dir = self.config.get('camera.capture_dir', 'captures')
        os.makedirs(self.capture_dir, exist_ok=True)

    def save_image(self, image, prefix: str = 'capture') -> Optional[str]:
        """Save image with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.capture_dir, f"{prefix}_{timestamp}.jpg")
            cv2.imwrite(filename, image)
            logger.info(f"Image saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Image save error: {str(e)}")
            return None

class DistanceFormatter:
    @staticmethod
    def format_distance(distance: float, unit: str = 'cm') -> str:
        """Format distance with units"""
        return f"{round(distance, 2)} {unit}"

class CredentialsManager:
    _instance = None
    CREDENTIALS_FILE = '.credentials'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CredentialsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.credentials = self.load_credentials()

    def load_credentials(self) -> dict:
        """Load credentials from hidden file"""
        try:
            if os.path.exists(self.CREDENTIALS_FILE):
                with open(self.CREDENTIALS_FILE, 'r') as f:
                    return json.load(f)
            else:
                default_credentials = {
                    'users': {
                        'admin': hashlib.sha256('admin123'.encode()).hexdigest()
                    }
                }
                self.save_credentials(default_credentials)
                return default_credentials
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return {'users': {}}

    def save_credentials(self, credentials: dict) -> bool:
        """Save credentials to hidden file"""
        try:
            with open(self.CREDENTIALS_FILE, 'w') as f:
                json.dump(credentials, f)
            if os.name == 'nt':  # Windows
                import subprocess
                subprocess.check_call(['attrib', '+h', self.CREDENTIALS_FILE])
            return True
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            return False

    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        if 'users' not in self.credentials:
            return False
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return (username in self.credentials['users'] and 
                self.credentials['users'][username] == hashed_password)

    def add_user(self, username: str, password: str) -> bool:
        """Add new user"""
        try:
            if 'users' not in self.credentials:
                self.credentials['users'] = {}
            
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.credentials['users'][username] = hashed_password
            return self.save_credentials(self.credentials)
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            return False

    def remove_user(self, username: str) -> bool:
        """Remove user"""
        try:
            if 'users' in self.credentials and username in self.credentials['users']:
                del self.credentials['users'][username]
                return self.save_credentials(self.credentials)
            return False
        except Exception as e:
            logger.error(f"Error removing user: {str(e)}")
            return False

# Initialize managers in correct order
config_manager = ConfigManager()
credentials_manager = CredentialsManager()

# Initialize services with dependencies
tts = TextToSpeech(config_manager)
image_handler = ImageHandler(config_manager)

# Export commonly used functions
speak = tts.speak
save_image = image_handler.save_image
format_distance = DistanceFormatter.format_distance
verify_credentials = credentials_manager.verify_credentials
add_user = credentials_manager.add_user
remove_user = credentials_manager.remove_user