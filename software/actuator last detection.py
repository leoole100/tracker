import serial
import zmq
import json
import cv2
import base64
import numpy as np
import time
import math
from threading import Thread

ser = serial.Serial('/dev/ttyACM0')

getAngle = lambda: float(ser.readline()) # 200 us
# setAngle = lambda a: ser.write(b'T'+bytes(f"{a:f}", "ascii")+b'\n') # 300us
def setAngle(a):
	if(a>0 and a<2*math.pi):
		ser.write(b'T'+bytes(f"{a:f}", "ascii")+b'\n')

rad_frame = 1.222 * np.array([1, 9/16]) / 2

a = np.pi
m = a
delta = 0
last = 0
delta_t = 0

def update_detection():
	global delta, last, delta_t, m
	context = zmq.Context()
	sub = context.socket(zmq.SUB)
	sub.connect("tcp://localhost:5556") # detector
	sub.setsockopt_string(zmq.SUBSCRIBE, "detection")

	while True:
		message = sub.recv_string()
		topic, data = message.split(" ", 1)

		data = json.loads(data)

		if data["valid"]:  
			delta = (0.5-data["center"][1])*rad_frame[1]		
			m = m + delta
			# t = data["time"]
			t = time.time()
			delta_t = last - t
			last = t


def main():
	while True:
		t = time.time()
		# if t-last > 0.1:
			# a = m
			#a = math.pi
			# ...
		# else:
			# a = m + delta * (last-t)/delta_t
		a = m # disable tracking
		setAngle(a)
		print(a)
			
		time.sleep(0.001)

if __name__ == "__main__":
	thread = Thread(target = update_detection)
	thread.start()
	main()
