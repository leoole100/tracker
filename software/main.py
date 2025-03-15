#%%
from tools import *
from matplotlib.pyplot import imshow
import numpy as np
from math import pi, cos
# %%
from camera import Camera
cam = Camera()
imshow(cam())

from detector import Detector
det = Detector()

measure_fps(lambda: det(cam()), N=100) # 190 Hz

# %%
from motor import Motor
 
m2 = Motor("/dev/serial/by-id/usb-Raspberry_Pi_Pico_504450612038C51C-if00")
m1 = Motor("/dev/serial/by-id/usb-Waveshare_RP2040_Zero_504450612862EA1C-if00")
# %%
pos = np.array([pi, pi])
m1(pos[0])
m2(pos[1])
time.sleep(0.2)

imshow(cam())

# %%
scale = 0.415
f = None
d = None
p = 0.1
threshold = 1e-200
def loop():
    global f, d, p 
    f = cam()
    d = det(f)
    if d["signal"] > threshold:
        error = (d["center"]-np.array([0.5, 0.5]))*scale*[4/3, 1]
        pos[0] += p*error[0]
        m1(pos[0])
        pos[1] -= p*error[1] * - cos(pos[0])
        m2(pos[1])

measure_fps(loop) # 180Hz

while True:
    loop()
    print(d)

# %%
# %%
# https://github.com/log0/video_streaming_with_flask_example