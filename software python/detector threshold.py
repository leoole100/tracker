import zmq
import json
import cv2
import base64
import numpy as np
import time
import math
from functions import decode, encode

def detect_cicle(img, 
	min_circularity=0.5,
	min_radius=1, 
	lower = np.array([  8, 130, 190]), 
	upper = np.array([ 12, 216, 246])
):
	img = cv2.GaussianBlur(img, (11, 11), 0)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(img, lower, upper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)


	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[0]

	best_contour = None
	max_circularity = -1

	for c in cnts:
		# Calculate area and perimeter
		area = cv2.contourArea(c)
		perimeter = cv2.arcLength(c, closed=True)

		# Skip small contours to avoid division by zero
		if perimeter == 0 or area < 3*min_radius**2:
			continue

		# Calculate circularity
		circularity = (4 * np.pi * area) / (perimeter ** 2)

		# Filter by circularity and radius
		(x, y), radius = cv2.minEnclosingCircle(c)
		if circularity > min_circularity and radius > min_radius:
			# Track the most circular contour (or use area as a tiebreaker)
			if circularity > max_circularity:
				max_circularity = circularity
				best_contour = c

	if best_contour is not None:
		color = img[mask.astype(bool)].mean(axis=0)
		print(color, "\t", max_circularity, area)
		return ((x/img.shape[1], y/img.shape[0]), radius)

	return False
	
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

			if frame.shape[0] == 0:
				break

			r = detect_cicle(frame)
			time_detection = time.time()

			if r:
				data = {
					"time": data["time"],
					"times": {
						**data["times"],
						"received": time_received - data["time"],
						"decoded": time_decoded - time_received,
						"detection": time_detection - time_decoded
					},
					"center": r[0],
					"size": r[1],
					"valid": True
				}
			else:
				data = {
					"time": data["time"],
					"times": {
						**data["times"],
						"received": time_received - data["time"],
						"decoded": time_decoded - time_received,
						"detection": time_detection - time_decoded
					},
					"valid": False
				}

			pub.send_string("detection " + json.dumps(data))
		
		elif topic == "detector_setting":
			print(data)
			if "threshold" in data:
				try:
					threshold = float(data["threshold"])
				except:
					pass


	sub.close()
	context.term()
	

if __name__ == "__main__":
	main()