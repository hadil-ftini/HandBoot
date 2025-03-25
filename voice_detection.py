import numpy as np
import pyaudio
import wave
import webrtcvad
import collections
import sys
import time
from array import array
from struct import pack
import logging

logger = logging.getLogger('VoiceBot')

class VoiceDetector:
    def __init__(self, 
                 rate=16000,
                 chunk_duration_ms=30,
                 padding_duration_ms=300,
                 threshold=0.3,
                 min_silence_duration=0.5):
                 
        self.rate = rate
        self.chunk_duration_ms = chunk_duration_ms
        self.padding_duration_ms = padding_duration_ms
        self.threshold = threshold
        self.min_silence_duration = min_silence_duration
        
        # Initialize VAD
        self.vad = webrtcvad.Vad(3)  # Aggressiveness level 3
        self.num_padding_chunks = int(padding_duration_ms / chunk_duration_ms)
        self.chunk_size = int(rate * chunk_duration_ms / 1000)
        self.ring_buffer = collections.deque(maxlen=self.num_padding_chunks)
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
    def is_speech(self, data):
        """Detect if audio chunk contains speech"""
        try:
            return self.vad.is_speech(data, self.rate)
        except:
            return False

    def normalize_audio(self, data):
        """Normalize audio data"""
        max_val = max(abs(max(data)), abs(min(data)))
        return [i/max_val for i in data] if max_val > 0 else data

    def record_with_vad(self, timeout=10):
        """Record audio with voice activity detection"""
        logger.info("Starting voice detection...")
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        silent_chunks = 0
        voiced_frames = []
        is_speaking = False
        start_time = time.time()

        try:
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    logger.info("Recording timeout reached")
                    break

                chunk = stream.read(self.chunk_size, exception_on_overflow=False)
                is_speech = self.vad.is_speech(chunk, self.rate)
                
                if is_speech:
                    logger.debug("Speech detected")
                    if not is_speaking:
                        is_speaking = True
                        # Add padding from before speech started
                        voiced_frames.extend([f for f in self.ring_buffer])
                    voiced_frames.append(chunk)
                    silent_chunks = 0
                else:
                    if is_speaking:
                        silent_chunks += 1
                        if silent_chunks > self.num_padding_chunks:
                            is_speaking = False
                            if len(voiced_frames) > 0:
                                return b''.join(voiced_frames)
                    
                    self.ring_buffer.append(chunk)

        except Exception as e:
            logger.error(f"Error in voice detection: {e}")
            return None
        finally:
            stream.stop_stream()
            stream.close()

    def save_audio(self, audio_data, filename="recorded_audio.wav"):
        """Save recorded audio to file"""
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.rate)
            wf.writeframes(audio_data)
            wf.close()
            logger.info(f"Audio saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            return False

    def cleanup(self):
        """Clean up resources"""
        self.audio.terminate()

def test_voice_detection():
    """Test voice detection system"""
    detector = VoiceDetector()
    print("Speak now (recording will stop after silence or timeout)...")
    
    audio_data = detector.record_with_vad()
    if audio_data:
        detector.save_audio(audio_data)
        print("Recording saved!")
    else:
        print("No speech detected!")
    
    detector.cleanup()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    # Test the voice detection
    test_voice_detection() 