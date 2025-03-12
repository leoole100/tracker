import cv2
import base64
import numpy as np

def encode(frame):
	ret, buffer = cv2.imencode('.jpg', frame)
	return base64.b64encode(buffer).decode('utf-8')

def decode(data):
	frame = data["image"]
	frame = base64.b64decode(frame)
	frame = np.frombuffer(frame, dtype=np.uint8)
	frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
	return frame