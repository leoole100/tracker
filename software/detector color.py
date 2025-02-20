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
	color = np.array([ 20.02,  49.74, 102.66]) # in rgb
	color_lab = np.array([ 69.42, 149.31, 156.84])

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

			# find weighted average by color distance
			grid = np.indices(frame.shape[:2]) 
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2Lab)
			# weights = frame/color_lab
			weights = 1/(frame - color_lab)
			weights = np.mean(weights[:,:,1:], 2)
			weights -= np.min(weights)
			weights = weights**10
			y = np.average(grid[0], weights=weights)
			x = np.average(grid[1], weights=weights)
			center = (x / frame.shape[1], y / frame.shape[0])
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
	
	except Exception as e:
		throw(e)

	finally:
		sub.close()
		context.term()
	

if __name__ == "__main__":
	main()