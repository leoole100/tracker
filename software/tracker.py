import zmq
import json
import cv2
import base64
import numpy as np

def main():
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect("tcp://localhost:5555") # frame publisher
	socket.setsockopt_string(zmq.SUBSCRIBE, "camera_frame")
	# socket.setsockopt_string(zmq.SUBSCRIBE, "tracker_settings")

	try:
		while True:
			# Wait for a message from the publisher
			message = socket.recv_string()
			topic, data = message.split(" ", 1)

			# Process the message based on topic
			if topic == "camera_frame":
				process_frame(data)
				pass
			elif topic == "tracker_settings":
				# Process the tracker settings
				pass
	except KeyboardInterrupt:
		print("Exiting...")
	finally:
		socket.close()
		context.term()

def process_frame(data):
	frame_data = json.loads(data)
	frame = frame_data["image"]
	frame = base64.b64decode(frame)
	frame = np.frombuffer(frame, dtype=np.uint8)
	frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
	print(frame.shape)

if __name__ == "__main__":
	main()