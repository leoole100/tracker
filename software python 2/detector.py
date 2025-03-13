# %%
import numpy as np
import numpy as np
from  base64 import b64decode, b64decode
import json, time, gc, zmq, cv2, os, sys
os.chdir(sys.path[0])

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
		return (np.array(amax)/np.array(self.w.shape))[::-1], snr

# %%



# %%
def main():
	cntx = zmq.Context()
	pub = cntx.socket(zmq.PUB)
	pub.bind("tcp://*:5002")
	sub = cntx.socket(zmq.SUB)
	sub.setsockopt_string(zmq.SUBSCRIBE, "camera")
	sub.connect("tcp://localhost:5001")
	sub.setsockopt(zmq.CONFLATE, 1)
	
	d = Detector()
	 
	while True:
		message = sub.recv_string()
		gc.disable()
		topic, data = message.split(" ", 1)
		data = json.loads(data)
	
		f = np.frombuffer(b64decode(data["buff"]), data["dtype"])
		f.shape = data["shape"]
  
		c, s = d(f)
  
		data = {
			"time": data["time"],
			"center": c,
			"snr": s
		}		
		pub.send_string("detection" + json.dumps("data"))
		gc.enable()
		gc.collect()

# %%
if __name__ == "__main__":
	main()