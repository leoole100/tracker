import serial
import zmq
import json
import cv2
import base64
import numpy as np
import time
import math
from threading import Thread
from queue import Queue

ser = serial.Serial('/dev/ttyACM0')

getAngle = lambda: float(ser.readline()) # 200 us
# setAngle = lambda a: ser.write(b'T'+bytes(f"{a:f}", "ascii")+b'\n') # 300us
def setAngle(a):
	if(a>0 and a<2*math.pi):
		ser.write(b'T'+bytes(f"{a:f}", "ascii")+b'\n')

rad_frame = 1.222 * np.array([1, 9/16]) / 2

