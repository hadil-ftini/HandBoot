import speech_recognition as sr
from utils import speak

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Dites quelque chose...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio, language="fr-FR")
            print(f"Vous avez dit : {command}")
            speak(f"Vous avez dit : {command}")
            return command
        except sr.UnknownValueError:
            speak("Je n'ai pas compris.")
            return "Commande non comprise"
        except sr.RequestError:
            speak("Erreur du service vocal.")
            return "Erreur de reconnaissance"
