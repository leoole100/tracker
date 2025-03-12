"""
Test to configure the pycamera2 api to get 200fps. Works in native python.
"""

#%%
from picamera2 import Picamera2
import time

c = Picamera2()
conf = 	c.create_preview_configuration(
	queue=False,
	buffer_count=2
)
c.start(conf)
c.set_controls({"FrameRate": 200})

def read_frame(c:Picamera2 = c):
    return c.capture_array()[...,:3]

#%%
N = 100
print(read_frame().shape)
start = time.time()
for i in range(N): read_frame()
print(f"{N/(time.time()-start) : .3g} fps")

# gives the requested 200 fps

# %%
c.stop()
