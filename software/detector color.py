import zmq
import json
import cv2
import base64
import numpy as np
import time


def main():
	context = zmq.Context()
	sub = context.socket(zmq.SUB)
	sub.connect("tcp://localhost:5555") # frame publisher
	sub.setsockopt_string(zmq.SUBSCRIBE, "camera_frame")

	pub = context.socket(zmq.PUB)
	pub.bind("tcp://*:5556")  

	# color range for object
	color = (182, 78, 71) # in rgb

	try:
		while True:
			# Wait for a message from the publisher
			message = sub.recv_string()
			topic, data = message.split(" ", 1)
			time_received = time.time()
			data = json.loads(data)

			# decode the frame
			frame = data["image"]
			frame = base64.b64decode(frame)
			frame = np.frombuffer(frame, dtype=np.uint8)
			frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
			time_decoded = time.time()


			# find the center of the orange blob
			# hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
			# grid = np.indices(hsv.shape[:2]) 
			# mask = cv2.inRange(hsv, color_lower, color_upper)
			# center = np.mean(grid[:, mask > 0], axis=1)
			# center = tuple(map(float, center[::-1] / frame.shape[:2][::-1]))
			# time_detection = time.time()


			# find weighted average by color distance
			grid = np.indices(frame.shape[:2]) 
			weights = np.linalg.norm(frame - color, axis=2)
			weights = 1 / (weights + 1)
			center = np.average(grid, weights=weights, axis=(1, 2))
			print(center)
			center = center[::-1] / frame.shape[:2][::-1]
			time_detection = time.time()

			data = {
				"time": data["time"],
				"times": {
					**data["times"],
					"received": time_received - data["time"],
					"decoded": time_decoded - time_received,
					"detection": time_detection - time_decoded
				},
				"center": center
			}
			pub.send_string("detection " + json.dumps(data))			
			
	finally:
		sub.close()
		context.term()
	

if __name__ == "__main__":
	main()