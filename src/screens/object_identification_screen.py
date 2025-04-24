from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

import cv2
import logging
import os
from ultralytics import YOLO

from ..components.custom_buttons import CustomButton
from ..utils.colors import COLORS


class ObjectIdentificationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_detecting = False
        self.detector = None
        self.cap = None
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Title
        title = Label(
            text="Object Identification",
            font_size='24sp',
            size_hint_y=None,
            height=50
        )

        # Camera view
        self.camera_view = Image(
            size_hint=(1, 0.7),
            allow_stretch=True,
            keep_ratio=True
        )

        # Results label
        self.result_label = Label(
            text="No object detected yet.",
            font_size='16sp',
            size_hint_y=None,
            height=100
        )

        # Identify button
        self.identify_button = CustomButton(
            text="Identify",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            color=(1, 1, 1, 1),
            background_color=COLORS['accent']
        )
        self.identify_button.bind(on_press=self.toggle_detection)


        # Back button
        back_button = CustomButton(
            text="Back",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            color=(1, 1, 1, 1),
            background_color=(0.2, 0.2, 0.2, 1)
        )
        back_button.bind(on_press=self.go_back)


        # Add all widgets
        layout.add_widget(title)
        layout.add_widget(self.camera_view)
        layout.add_widget(self.result_label)
        layout.add_widget(self.identify_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def toggle_detection(self, instance):
        if not self.is_detecting:
            # Start detection
            self.is_detecting = True
            self.identify_button.text = "Stop"
            self.identify_button.background_color = COLORS['warning']
            self.start_detection()
        else:
            # Stop detection
            self.stop_detection()
            

    def start_detection(self):
        try:
            # Initialize camera
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise Exception("Could not open camera")

            # Test camera reading
            ret, frame = self.cap.read()
            if not ret or frame is None:
                raise Exception("Could not read from camera")


            # Start camera preview first
            self.event = Clock.schedule_interval(self.update_camera, 1.0/30.0)
            self.update_status_label("Camera initialized. Loading model...")

            # Load model in a separate thread to prevent UI freezing
            import threading
            self.model_thread = threading.Thread(target=self.load_model, daemon=True)
            self.model_thread.start()
        except Exception as e:
            self.update_error_label(f"Camera Error: {str(e)}")
            self.stop_detection()
            

    
    def stop_detection(self):
        try:
            # Cancel the update event if it exists
            if self.event:
                self.event.cancel()
                self.event = None

            # Release the camera if it exists
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                self.cap = None

            # Reset the model
            self.model = None
            # Reset UI elements
            self.is_detecting = False
            self.identify_button.text = "Identify"
            self.identify_button.background_color = COLORS['accent']
            self.camera_view.texture = None
            
        except Exception as e:
            print(f"Error in stop_detection: {str(e)}")
    def update_camera(self, dt):
        if not self.is_detecting or self.cap is None:
            return False

        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.update_error_label("Error: Could not read frame")
                return False

            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)

            # Convert the frame to texture
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            
            # Update the camera view
            self.camera_view.texture = texture

            # If model is loaded, perform detection
            if self.model is not None:
                try:
                    self.process_frame(frame)
                except Exception as e:
                    self.update_error_label(f"Detection error: {str(e)}")
                    return False

            return True

        except Exception as e:
            self.update_error_label(f"Camera error: {str(e)}")
            return False

    def process_frame(self, frame):
        if self.model is None:
            return

        try:
            # Convert frame to RGB (YOLO expects RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run inference
            results = self.model(frame_rgb)
            
            # Process detections
            detected_objects = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Get confidence and class
                    conf = box.conf.cpu().numpy()[0]
                    cls = int(box.cls.cpu().numpy()[0])
                    
                    if conf > 0.25:  # Confidence threshold
                        label = f"{result.names[cls]} {conf:.2f}"
                        detected_objects.append(label)
                        
                        # Convert coordinates to integers
                        c1 = (int(x1), int(y1))
                        c2 = (int(x2), int(y2))
                        
                        # Draw box with thicker lines
                        cv2.rectangle(frame, c1, c2, (0, 255, 0), 3)
                        
                        # Add background to text for better visibility
                        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                        cv2.rectangle(frame, (c1[0], c1[1] - text_size[1] - 4),
                                    (c1[0] + text_size[0], c1[1]), (0, 255, 0), -1)
                        cv2.putText(frame, label, (c1[0], c1[1] - 2),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

            # Update result label with detected objects
            if detected_objects:
                self.update_status_label("Detected: " + ", ".join(detected_objects))
            else:
                self.update_status_label("No objects detected")

            # Update the display with the annotated frame
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.camera_view.texture = texture

        except Exception as e:
            import traceback
            error_msg = f"Processing error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)  # Print to console for debugging
            self.update_error_label(error_msg)

    def on_leave(self):
        """Called when leaving the screen"""
        self.stop_detection()

    def go_back(self, instance):
        self.stop_detection()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

    def update_error_label(self, error_message):
        """Helper method to update error label from main thread"""
        def update(dt):
            self.result_label.text = error_message
            if self.is_detecting:
                self.stop_detection()
        Clock.schedule_once(update)

    def update_status_label(self, status_message):
        """Helper method to update status label from main thread"""
        def update(dt):
            self.result_label.text = status_message
        Clock.schedule_once(update)

    def load_model(self):
        try:
            import torch
            import sys
            import logging
            import os
            from ultralytics import YOLO
            
            # Configure logging
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            
            # Update UI to show loading status
            self.update_status_label("Loading YOLOv5 model...")
            logger.info("Starting model load")
            
            try:
                # Get the path to the local model file
                model_path = os.path.join(os.path.dirname(__file__), 'yolov5s.pt')
                logger.info(f"Loading model from: {model_path}")
                
                # Load the model using YOLO
                self.model = YOLO(model_path)
                
                logger.info("Model loaded successfully")
                
                # Update UI
                self.update_status_label("Model loaded successfully. Starting detection...")
                
            except Exception as model_error:
                logger.error(f"Error loading model: {str(model_error)}")
                logger.error(f"Python path: {sys.path}")
                raise model_error
                
        except Exception as e:
            error_msg = f"Error in load_model: {str(e)}"
            logger.error(error_msg)
            self.update_error_label(error_msg)

    