import os
import sys
import time

def print_header(text):
    print("\n" + "="*50)
    print(text.center(50))
    print("="*50 + "\n")

def run_test(test_name, test_module):
    print_header(f"Running {test_name}")
    try:
        __import__(test_module)
        print(f"\n{test_name} completed!")
        return True
    except Exception as e:
        print(f"\n{test_name} failed: {str(e)}")
        return False

def main():
    print_header("VoiceBot System Tests")
    
    # Test TTS
    tts_success = run_test("TTS Test", "test_tts")
    time.sleep(2)  # Wait for TTS to finish
    
    # Test Microphone
    mic_success = run_test("Microphone Test", "test_mic")
    time.sleep(2)  # Wait between tests
    
    # Test Complete Audio System
    audio_success = run_test("Complete Audio System Test", "test_audio_system")
    
    # Print Summary
    print_header("Test Summary")
    print(f"TTS Test: {'✓' if tts_success else '✗'}")
    print(f"Microphone Test: {'✓' if mic_success else '✗'}")
    print(f"Audio System Test: {'✓' if audio_success else '✗'}")
    
    if all([tts_success, mic_success, audio_success]):
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed. Please check the logs above.")

if __name__ == "__main__":
    main() 