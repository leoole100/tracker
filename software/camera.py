import zmq
import time
import json
import cv2
from functions import encode

def setup_camera(cap):
		# Set camera properties
		# assert cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
		assert cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Set codec to MJPG for compression	
		assert cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
		assert cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
		assert cap.set(cv2.CAP_PROP_FPS, 30)

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

		# cap = cv2.VideoCapture(0)
		cap = cv2.VideoCapture(2)


		cap = setup_camera(cap)

		while True:
			# take a frame
			ret, frame = cap.read()
			frame_time = time.time()

			# Encode the frame as JPEG 
			jpg_as_text = encode(frame)
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
