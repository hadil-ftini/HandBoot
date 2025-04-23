import cv2
import torch
import numpy as np
import os

class ObjectDetector:
    def __init__(self):
        try:
            # Initialize YOLOv5 model
            print("Loading YOLOv5 model...")
            self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, trust_repo=True)
            self.model.conf = 0.5  # Confidence threshold
            self.model.iou = 0.45  # NMS IoU threshold
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise

    def detect_objects(self, frame):
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Perform inference
            results = self.model(rgb_frame)
            
            # Process detections
            detections = []
            
            # Get detection results
            for det in results.xyxy[0]:  # xyxy format: x1, y1, x2, y2, confidence, class
                x1, y1, x2, y2, conf, cls = det.tolist()
                
                # Convert coordinates to integers
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                
                # Get class name
                class_name = self.model.names[int(cls)]
                
                detections.append({
                    'class': class_name,
                    'confidence': conf,
                    'box': (x1, y1, x2, y2)
                })
                
                # Draw detection on frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f'{class_name}: {conf:.2f}'
                cv2.putText(frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            return frame, detections
        except Exception as e:
            print(f"Error in detect_objects: {str(e)}")
            raise