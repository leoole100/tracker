# %%
import numpy as np
import numpy as np
from  base64 import b64decode, b64decode
import json, time, gc, zmq, cv2, os, sys

class Detector():
	# size = (160, 120)
	size = (80, 60)
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