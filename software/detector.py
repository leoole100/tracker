# %%
import numpy as np
import numpy as np
from  base64 import b64decode, b64decode
import json, time, gc, zmq, cv2, os, sys

class Detector():
	# size = (160, 120)
	size = (40, 30)
	def __init__(self):
		template = cv2.imread("../ball.png")
		template_lab = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
		self.mean = np.mean(template_lab, axis=(0,1))
		self.std = np.std(template_lab, axis=(0,1))

	# 3.6 ms
	def __call__(self, f):
		self.f_small = cv2.resize(f, self.size)
		self.fc = cv2.cvtColor(self.f_small, cv2.COLOR_RGB2HSV)
		self.diff = self.fc - self.mean
		self.w = np.mean(self.diff**2 / self.std, axis=2)
		self.w = np.exp(-self.w)
		amax = np.unravel_index(self.w.argmax(), self.w.shape)
		return {
      		"center": (np.array(amax)/np.array(self.w.shape))[::-1].tolist(),
			"signal": self.w[amax]
		}
#%%
from queue import Queue, Empty # Thread save queue (not interprocess)
from threading import Thread

class DetectorThread():
    def __init__(self, camera):
        self.output = Queue(1)
        self.running = True
        self.cam = camera
        self.detector = Detector()
        self.thread = Thread(target=self.task)
        self.thread.start()
    
    def task(self):
        while self.running:
            t = self.detector(self.cam())

            # empty queue if not used
            try: self.output.get_nowait()
            except Empty: pass
            self.output.put(t)

    def stop(self):
        self.running = False
        self.thread.join()
        self.cam.__del__()

    def __del__(self):
        self.stop()

    def __call__(self):
        if self.running: return self.output.get()