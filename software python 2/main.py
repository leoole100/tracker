# %%
from camera import Camera
from detector import Detector
from motor import Motor
from math import pi

c = Camera()
d = Detector()
m = Motor()


# %%
Threshold = 25
Scale = 0.415
a = pi
P = 0.2
f = c()

# %%
from threading import Thread
from IPython.display import display, Image
import cv2
import time

def stream():
	global f
	disp=display(None, display_id=True)
	i = 0
	while True:
		_, frame = cv2.imencode('.jpeg', f[..., ::-1])
		disp.update(Image(data=frame.tobytes()))
		time.sleep(0.05)
s = Thread(target=stream)
s.start()
# %%
# 8 ms
def loop():
	global a
	global f
	f = c()
	center, snr = d(f)
	print(	center, snr)
	if snr > 1000:
		error = center[1] / d.size[1] - 0.5
		a += error*Scale*P
		m(a)
	
def run():
	while True:
		loop()

run()
# %%
