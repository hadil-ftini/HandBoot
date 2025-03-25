# Tests basic speech output
# Tests French language
# Tests volume control
# When to use: When having issues with voice output or TTS

import pyttsx3
import time

def test_tts():
    print("Testing TTS...")
    
    # Initialize engine
    try:
        engine = pyttsx3.init()
        print("TTS engine initialized successfully")
        
        # Test basic speech
        print("Testing basic speech...")
        engine.say("Test 1 2 3")
        engine.runAndWait()
        time.sleep(1)
        
        # Test French
        print("Testing French speech...")
        engine.say("Bonjour, comment allez-vous?")
        engine.runAndWait()
        time.sleep(1)
        
        # Test volume
        print("Testing volume...")
        engine.setProperty('volume', 1.0)
        engine.say("Test volume maximum")
        engine.runAndWait()
        
        print("TTS test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing TTS: {str(e)}")
        return False

if __name__ == "__main__":
    test_tts() 