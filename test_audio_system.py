# Functions:
# Tests speakers (TTS output)
# Tests microphone recording
# Tests speech recognition
# Lists available audio devices
# When to use: To verify all audio components are working together

import pyaudio
import wave
import time
import speech_recognition as sr
import pyttsx3
import os

def test_speakers():
    """Test audio output with TTS"""
    print("\nTesting speakers...")
    try:
        # Try pyttsx3
        engine = pyttsx3.init()
        engine.say("Testing speakers with text to speech")
        engine.runAndWait()
        
        # Try espeak directly
        os.system('espeak "Testing speakers with espeak"')
        
        return True
    except Exception as e:
        print(f"Speaker test failed: {str(e)}")
        return False

def test_microphone():
    """Test microphone recording"""
    print("\nTesting microphone...")
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 3
    WAVE_OUTPUT_FILENAME = "test_recording.wav"

    try:
        p = pyaudio.PyAudio()
        
        # List audio devices
        print("\nAvailable audio devices:")
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            print(f"Device {i}: {dev['name']}")

        print(f"\nRecording {RECORD_SECONDS} seconds of audio...")
        
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

        print("Playing back recording...")
        os.system(f"aplay {WAVE_OUTPUT_FILENAME}")
        
        return True
    except Exception as e:
        print(f"Microphone test failed: {str(e)}")
        return False

def test_speech_recognition():
    """Test speech recognition"""
    print("\nTesting speech recognition...")
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("Please say 'test'...")
            audio = recognizer.listen(source, timeout=5)
            
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            
            # Confirm what was heard
            engine = pyttsx3.init()
            engine.say(f"I heard: {text}")
            engine.runAndWait()
            
            return True
            
    except Exception as e:
        print(f"Speech recognition test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting complete audio system test...")
    
    # Test speakers
    if test_speakers():
        print("Speaker test passed!")
    else:
        print("Speaker test failed!")
    
    # Test microphone
    if test_microphone():
        print("Microphone test passed!")
    else:
        print("Microphone test failed!")
    
    # Test speech recognition
    if test_speech_recognition():
        print("Speech recognition test passed!")
    else:
        print("Speech recognition test failed!")
    
    print("\nTest complete! Check the results above to see what's working.") 