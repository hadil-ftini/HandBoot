import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import pyttsx3
from kivy.graphics.texture import Texture

# Speech engine
engine = pyttsx3.init()

TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

cap = cv2.VideoCapture(0)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.1)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def capture_image():
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("captured_image.jpg", frame)
        speak("Image capturée avec succès.")
