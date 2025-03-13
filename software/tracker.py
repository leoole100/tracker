# %%
from camera import Camera
c = Camera()
from motor import Motor
m = Motor()
from math import pi
from detector import Detector
d = Detector()

# %%
# 8 m
Threshold = 1e-5
hysteresis = 10
Scale = 0.415
P = 0.2
f = c()
a = pi
tracking = False
m(a)

# 5 ms
def loop():
    global a, f, tracking
    f = c()
    det = d(f)
    if (tracking and det["signal"] > Threshold) or (not tracking and det["signal"] > Threshold*hysteresis):
        error = det["center"][1] - 0.5
        a += error*Scale*P
        m(a)
        tracking = True
    else:
        tracking = False
    print(tracking, det["signal"], a)
    
def run():
    while True:
        loop()

run()
# %%
