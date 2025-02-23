import zmq
import json
import cv2
import base64
import numpy as np
import time
import math
from functions import decode, encode
import skimage as ski

def detect(frame,
	color=cv2.cvtColor(np.uint8([[[249,166,106]]]),cv2.COLOR_RGB2LAB)[0,0],
	w = [128, 10, 10],
	k = np.ones((5,5))
):
	frame_lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
	mask = cv2.inRange(frame_lab, color-w, color+w)
	mask = cv2.erode(mask, k, iterations=2)
	mask = cv2.dilate(mask, k, iterations=2)

	cont, hir = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

	if len(cont) == 0:
		return frame, (0.5, 0.5), -1000.

	cnt = max(cont, key=cv2.contourArea)
	M = cv2.moments(cnt)
	c = [M['m10']/M['m00']/frame.shape[1], M['m01']/M['m00']/frame.shape[0]]

	signal = np.sum((cv2.mean(frame_lab, mask)[:3] - color)**2)
	signal = -10*math.log10(signal)
	
	return (1 + mask[:,:,None]/255)*frame[:,:,::]/2, c, signal

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

			mask, c, signal = detect(frame)
			time_detection= time.time()

			data = {
				"time": data["time"],
				"times": {
					**data["times"],
					"received": time_received - data["time"],
					"decoded": time_decoded - time_received,
					"detection": time_detection - time_decoded
				},
				"center": c,
				"contrast": signal,
				"valid": (signal>threshold),
				"mask": encode(mask)
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