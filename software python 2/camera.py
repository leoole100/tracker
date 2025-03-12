# %%
from picamera2 import Picamera2

class Camera:
	def __init__(self):
		self.c = Picamera2()
		conf = 	self.c.create_preview_configuration(
			queue=False,
			buffer_count=2
		)
		self.c.start(conf)
		self.c.set_controls({"FrameRate": 200})
  
	def __del__(self):
		self.c.stop()
		self.c.close()
  
	def __call__(self):
		return self.c.capture_array()[...,:3]