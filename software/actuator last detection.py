import serial
import zmq
import json
import cv2
import base64
import numpy as np
import time
import math

ser = serial.Serial('/dev/ttyACM0')

getAngle = lambda: float(ser.readline()) # 200 us
def setAngle(a):
	if(a>=0 and a<2*math.pi):
		ser.write(b'T'+bytes(f"{a:f}", "ascii")+b'\n')
		return True
	return False
rad_frame = 0.541 * np.array([16/9, 1])


def main():
    
	context = zmq.Context()
	sub = context.socket(zmq.SUB)
	sub.connect("tcp://localhost:5556") # detector
	sub.setsockopt_string(zmq.SUBSCRIBE, "detection")
	sub.setsockopt(zmq.CONFLATE, 1) # take most recent

	a = math.pi
	setAngle(a)
	while True:
		message = sub.recv_string()
		topic, data = message.split(" ", 1)

		data = json.loads(data)

		if data["valid"]:
			a += (data["center"][1]-0.5)/2*rad_frame[1]		
			setAngle(a)
			

if __name__ == "__main__":
	main()
