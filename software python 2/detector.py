# %%
import cv2
import numpy as np

class Detector():
	size = (160, 120)
	def __init__(self):
		template = cv2.imread("../ball.png")
		template_lab = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
		self.mean = np.mean(template_lab, axis=(0,1))
		self.std = np.std(template_lab, axis=(0,1))

	# 5 ms
	def __call__(self, f):
		self.f_small = cv2.resize(f, self.size)
		self.fc = cv2.cvtColor(self.f_small, cv2.COLOR_RGB2HSV)
		self.diff = self.fc - self.mean
		self.w = - np.mean(self.diff**2 / self.std, axis=2)
		self.w = np.exp(self.w)
		amax = np.unravel_index(self.w.argmax(), self.w.shape)
		snr = self.w[amax] / np.mean(self.w)
		return amax[::-1], snr