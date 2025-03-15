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
	
	def close(self):
		self.c.stop()
		self.c.close()

	def __del__(self):
		self.close()
  
	def __call__(self):
		return self.c.capture_array()[::-1, ::-1,:3]
	
# %%
# %%
from queue import Queue, Empty # Thread save queue (not interprocess)
from threading import Thread
class CameraThread():
    def __init__(self):
        self.last_frame = Queue(1)
        self.running = True
        self.camera = Camera()
        self.task = Thread(target=self.read_frames)
        self.task.start()
    
    def read_frames(self):
        while self.running:
            f = self.camera()

            # empty queue if not used
            try: self.last_frame.get_nowait()
            except Empty: pass

            self.last_frame.put(f)

    def stop(self):
        self.running = False
        self.task.join()
        self.camera.close()

    def __del__(self):
        self.stop()

    def __call__(self):
        if self.running: return self.last_frame.get()
