import pyaudio
import wave
import time
import numpy as np
from array import array
import logging

logger = logging.getLogger('VoiceBot')

class SimpleVoiceDetector:
    def __init__(self,
                 threshold=500,
                 silence_threshold=30,
                 rate=16000,
                 chunk_size=1024):
        self.threshold = threshold
        self.silence_threshold = silence_threshold
        self.rate = rate
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
    def is_silent(self, data_chunk):
        """Returns 'True' if below the 'silent' threshold"""
        return max(data_chunk) < self.threshold

    def normalize(self, data_all):
        """Average the volume out"""
        times = float(self.rate) / len(data_all)
        data_all = np.multiply(data_all, times)
        return data_all

    def record_voice(self, timeout=10):
        """Record voice with simple voice activity detection"""
        logger.info("Starting voice recording...")
        
        stream = self.audio.open(
            format=self.format,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        silent_chunks = 0
        voiced_frames = []
        is_speaking = False
        start_time = time.time()

        print("Listening...")

        try:
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    logger.info("Recording timeout reached")
                    break

                # Read chunk and convert to integers
                chunk = stream.read(self.chunk_size, exception_on_overflow=False)
                data_chunk = array('h', chunk)
                
                # Check volume
                if max(data_chunk) > self.threshold:
                    if not is_speaking:
                        logger.debug("Speech detected")
                        is_speaking = True
                    silent_chunks = 0
                    voiced_frames.append(chunk)
                else:
                    if is_speaking:
                        silent_chunks += 1
                        if silent_chunks > self.silence_threshold:
                            break
                    voiced_frames.append(chunk)

                # Break if enough silence or enough audio
                if len(voiced_frames) > 100 and silent_chunks > self.silence_threshold:
                    break

        except Exception as e:
            logger.error(f"Error recording: {e}")
            return None

        finally:
            stream.stop_stream()
            stream.close()

        if voiced_frames:
            return b''.join(voiced_frames)
        return None

    def save_audio(self, audio_data, filename="recorded_audio.wav"):
        """Save recorded audio to file"""
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
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
    """Test the voice detection system"""
    detector = SimpleVoiceDetector()
    print("Please speak something...")
    
    audio_data = detector.record_voice(timeout=5)
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