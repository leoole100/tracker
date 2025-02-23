import cv2
import base64
import numpy as np

def setup_camera(cap):
		# Set camera properties
		# assert cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
		assert cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
		assert cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
		assert cap.set(cv2.CAP_PROP_FPS, 30)
		assert cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Set codec to MJPG for compression	

		if not cap.isOpened():
				print("Error: Cannot open camera")
				return
		
		ret, frame = cap.read()
		assert ret, "Error: Cannot read camera frame"
		print("Camera frame shape:", frame.shape)
	
		return cap

def encode(frame):
	ret, buffer = cv2.imencode('.jpg', frame)
	return base64.b64encode(buffer).decode('utf-8')

def decode(data):
	frame = data["image"]
	frame = base64.b64decode(frame)
	frame = np.frombuffer(frame, dtype=np.uint8)
	frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
	return frame