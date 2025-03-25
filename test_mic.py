# Records audio
# Tests speech recognition
# Lists available microphones
# When to use: When having issues with voice input or microphone

import pyaudio
import wave
import time
import speech_recognition as sr

def test_recording():
    """Test basic audio recording"""
    print("Testing microphone recording...")
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 3
    WAVE_OUTPUT_FILENAME = "test_recording.wav"

    p = pyaudio.PyAudio()

    print("Recording 3 seconds of audio...")
    
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"Audio saved to {WAVE_OUTPUT_FILENAME}")
    return True

def test_speech_recognition():
    """Test speech recognition"""
    print("\nTesting speech recognition...")
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("Say something...")
            audio = recognizer.listen(source, timeout=5)
            
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return True
            
    except sr.WaitTimeoutError:
        print("No speech detected")
        return False
    except sr.UnknownValueError:
        print("Could not understand audio")
        return False
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting microphone tests...")
    
    # Test basic recording
    if test_recording():
        print("\nBasic recording test passed!")
        # Play back the recording
        print("Playing back recording...")
        import os
        os.system("aplay test_recording.wav")
    else:
        print("\nBasic recording test failed!")
    
    # Test speech recognition
    if test_speech_recognition():
        print("\nSpeech recognition test passed!")
    else:
        print("\nSpeech recognition test failed!") 