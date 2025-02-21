import zmq
import json
import cv2
import base64
import numpy as np
import time

def center_of_mass(frame, color=np.array([ 69.42, 149.31, 156.84])):
	frame_lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
	diff = frame_lab.astype(np.float32) - color.astype(np.float32)
	weights = np.sum(diff[:,:,1:], axis=2)
	weights = np.exp(weights)
	weights -= np.min(weights)
	total = np.sum(weights)
	indices = np.indices(weights.shape)
	x = np.sum(indices[1] * weights) / total
	y = np.sum(indices[0] * weights) / total

	return weights, (x, y)


def main():
	context = zmq.Context()
	sub = context.socket(zmq.SUB)
	sub.setsockopt(zmq.CONFLATE, 1) # take most recent
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
			_, c = center_of_mass(frame)
			center = (c[0]/frame.shape[1], c[1]/frame.shape[0])
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