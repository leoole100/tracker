import zmq
import json
import cv2
import base64
import numpy as np
import time
import math
from functions import decode, encode
import skimage as ski


def center_of_mass(frame, color=np.array([ 75*255/100, 24.7+128, 43.26+128]), w=10):
	frame_lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
	diff = frame_lab - color.astype(frame_lab.dtype)
	weights = np.sum(diff[:,:,1:]**2, axis=2)
	weights = np.exp(-weights/w)
	contrast = np.max(weights) - np.mean(weights)
	total = np.sum(weights)
	indices = np.indices(weights.shape)
	x = np.sum(indices[1] * weights) / total
	y = np.sum(indices[0] * weights) / total
	var_x = np.sum(weights * ((indices[1] - x) ** 2)) / total
	var_y = np.sum(weights * ((indices[0] - y) ** 2)) / total
	spread = np.sqrt(var_x + var_y)
  
	return weights, (x, y), spread, contrast


def main():
	context = zmq.Context()
	sub = context.socket(zmq.SUB)
	sub.connect("tcp://localhost:5555") # frame publisher
	sub.connect("tcp://localhost:5550") # viewer
	sub.setsockopt_string(zmq.SUBSCRIBE, "camera_frame")
	sub.setsockopt_string(zmq.SUBSCRIBE, "detector_setting")
	# sub.setsockopt(zmq.CONFLATE, 1) # take most recent

	pub = context.socket(zmq.PUB)
	pub.bind("tcp://*:5556")  

	threshold = -100

	while True:
		# Wait for a message from the publisher
		message = sub.recv_string()
		topic, data = message.split(" ", 1)

		time_received = time.time()
		data = json.loads(data)

		if topic == "camera_frame":
			# decode the frame
			frame = decode(data)
			time_decoded = time.time()

			# find weighted average by color distance
			frame_scaled = cv2.resize(frame, (frame.shape[1]//2, frame.shape[0]//2))
			weight, c, s, contrast = center_of_mass(frame_scaled)
			center = (c[0]/frame_scaled.shape[1], c[1]/frame_scaled.shape[0])
			spread = s/frame_scaled.shape[1]
			contrast = 10*float(np.log10(contrast))
			weight_as_text = encode(weight)
			time_detection = time.time()

			data = {
				"time": data["time"],
				"times": {
					**data["times"],
					"received": time_received - data["time"],
					"decoded": time_decoded - time_received,
					"detection": time_detection - time_decoded
				},
				"weight": weight_as_text,
				"center": center,
				"size":  spread,
				"contrast": contrast,
				"valid": (contrast>threshold),
			}
			pub.send_string("detection " + json.dumps(data))
		
		elif topic == "detector_setting":
			print(data)
			if "threshold" in data:
				threshold = float(data["threshold"])


	sub.close()
	context.term()
	

if __name__ == "__main__":
	main()