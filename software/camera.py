import cv2
import zmq
import base64
import time
import json

def setup_camera():
		# Open the camera (usually device 0)
		cap = cv2.VideoCapture(0)

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

def main():
		# Set up ZeroMQ publisher
		context = zmq.Context()
		socket = context.socket(zmq.PUB)
		socket.bind("tcp://*:5555")  # Bind to port 5555

		cap = setup_camera()

		while True:
			# take a frame
			ret, frame = cap.read()
			frame_time = time.time()

			# Encode the frame as JPEG
			ret, buffer = cv2.imencode('.jpg', frame)
			jpg_as_text = base64.b64encode(buffer).decode('utf-8')
			encoding_time = time.time()
			
			# create a json dict with times and data
			data = {
				"time": frame_time,
				"times": {
					"encoding": encoding_time - frame_time,
				},
				"image": jpg_as_text,
			}
			socket.send_string("camera_frame " + json.dumps(data))

if __name__ == '__main__':
		main()
