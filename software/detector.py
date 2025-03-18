# %%
import numpy as np
import numpy as np
import cv2
import math
from glob import glob

def log10_clamp(a):
	if a<=0: return -9999999999
	return math.log10(a)

class Detector():
	# size = (160, 120)
	size = (80, 60)
	def __init__(self):
		templates = [cv2.imread(p) for p in glob("*.png")]
		templates_lab = [cv2.cvtColor(i, cv2.COLOR_BGR2HSV) for i in templates]
		lab = np.concatenate([t.reshape(t.shape[0]*t.shape[1], 3) for t in templates_lab])
		self.mean = np.mean(lab, axis=0)
		self.std = np.std(lab, axis=0)

	# 3.6 ms
	def __call__(self, f):
		self.f_small = cv2.resize(f, self.size)
		self.fc = cv2.cvtColor(self.f_small, cv2.COLOR_RGB2HSV)
		self.diff = self.fc - self.mean
		self.w = np.mean(self.diff**2 /self.std, axis=2)
		self.w = np.exp(-self.w)
		amax = np.unravel_index(self.w.argmax(), self.w.shape)
		signal = log10_clamp(self.w[amax])*10
		# snr = log10_clamp(signal/np.mean(self.w))*10
		return {
      		"center": (np.array(amax)/np.array(self.w.shape))[::-1].tolist(),
			"signal": signal,
			# "snr": snr
		}