# mock_gpio.py

import time

# Mock RPi.GPIO module
class MockGPIO:
    BCM = "BCM"
    OUT = "OUT"
    IN = "IN"
    
    def setmode(self, mode):
        print(f"GPIO mode set to {mode}")
    
    def setup(self, pin, mode):
        print(f"Pin {pin} set to {mode}")
    
    def output(self, pin, state):
        print(f"Pin {pin} output set to {state}")
    
    def input(self, pin):
        time.sleep(0.01)  # Simulating sensor delay
        return 1  # Mocked high signal
    
    def cleanup(self):
        print("GPIO cleanup")

# Replace RPi.GPIO with the mock
GPIO = MockGPIO()
