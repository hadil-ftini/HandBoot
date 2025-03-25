from typing import Dict, Optional
import json
import os

class LanguageManager:
    # Supported languages with their codes
    SUPPORTED_LANGUAGES = {
        'fr': {
            'name': 'Français',
            'code': 'fr-FR',
            'voice': 'french',
            'rate': 150
        },
        'en': {
            'name': 'English',
            'code': 'en-US',
            'voice': 'english',
            'rate': 150
        },
        'ar': {
            'name': 'العربية',
            'code': 'ar-SA',
            'voice': 'arabic',
            'rate': 150
        },
        'es': {
            'name': 'Español',
            'code': 'es-ES',
            'voice': 'spanish',
            'rate': 150
        }
    }

    def __init__(self):
        self.current_language = 'fr'
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        """Load all language translations"""
        try:
            for lang_code in self.SUPPORTED_LANGUAGES.keys():
                file_path = f'translations/{lang_code}.json'
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
        except Exception as e:
            print(f"Error loading translations: {e}")

    def get_text(self, key: str, lang_code: Optional[str] = None) -> str:
        """Get translated text for a key"""
        lang = lang_code or self.current_language
        try:
            return self.translations[lang][key]
        except:
            return key

    def set_language(self, lang_code: str) -> bool:
        """Change current language"""
        if lang_code in self.SUPPORTED_LANGUAGES:
            self.current_language = lang_code
            return True
        return False

    def get_current_language_code(self) -> str:
        """Get current language code for speech recognition"""
        return self.SUPPORTED_LANGUAGES[self.current_language]['code']

    def get_current_voice(self) -> str:
        """Get current voice for TTS"""
        return self.SUPPORTED_LANGUAGES[self.current_language]['voice']

    def get_speech_rate(self) -> int:
        """Get speech rate for current language"""
        return self.SUPPORTED_LANGUAGES[self.current_language]['rate']

# Create translations directory and example files
os.makedirs('translations', exist_ok=True)

# French translations
fr_translations = {
    'welcome': 'Bienvenue',
    'goodbye': 'Au revoir',
    'speak_now': 'Parlez maintenant',
    'not_understood': 'Je n\'ai pas compris',
    'try_again': 'Veuillez réessayer',
    'processing': 'Traitement en cours',
    'error': 'Erreur',
    'success': 'Succès'
}

# English translations
en_translations = {
    'welcome': 'Welcome',
    'goodbye': 'Goodbye',
    'speak_now': 'Speak now',
    'not_understood': 'I didn\'t understand',
    'try_again': 'Please try again',
    'processing': 'Processing',
    'error': 'Error',
    'success': 'Success'
}

# Save translation files
with open('translations/fr.json', 'w', encoding='utf-8') as f:
    json.dump(fr_translations, f, ensure_ascii=False, indent=4)

with open('translations/en.json', 'w', encoding='utf-8') as f:
    json.dump(en_translations, f, ensure_ascii=False, indent=4)

# Initialize language manager
language_manager = LanguageManager() 