# %%
from camera import Camera
c = Camera()
from motor import Motor
# m = Motor()
from math import pi

# %%
from detector import Detector
d = Detector()

# %%
# 8 m
Threshold = 25
Scale = 0.415
P = 0.3
f = c()
a = pi
# m(a)
def loop():
    global a
    global f
    f = c()
    det = d(f)
    print(det["signal"])
    if det["signal"] > 1e-6:
        error = det["center"][1] - 0.5
        a += error*Scale*P
        # m(a)
    
def run():
    while True:
        loop()

run()
# %%
