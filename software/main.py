#%%
from queue import Queue, Empty # Thread save queue (not interprocess)
from threading import Thread
import time


# %%
from camera import CameraThread
cam = CameraThread()

# from matplotlib.pyplot import imshow
# imshow(cam())
# %time f = cam(); # 25us
# %timeit f = cam(); # 5ms

# %%
from detector import Detector, DetectorThread
detector = Detector()
# %timeit detector(f); # 4.6ms


# %%
dt = DetectorThread(cam)
# %timeit dt() #5ms

# %%
dt()