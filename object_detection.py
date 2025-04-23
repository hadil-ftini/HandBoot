# object_detection.py

import cv2
import torch

def detect_objects():
    # Open the default camera
    cap = cv2.VideoCapture(0)

    # Load the YOLOv5 model
    #model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Perform object detection
        #results = model(frame)
        #results.render()

        # Show the frame with detection boxes
        #cv2.imshow("Object Detection", results.imgs[0])

        # Print detected object names in console (optional)
        #detected_objects = results.pandas().xywh[0]
        #if not detected_objects.empty:
            print("Detected objects:", ', '.join(detected_objects['name']))

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
