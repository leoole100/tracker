#%%
from tools import *
import numpy as np
from math import pi, cos
import json
from flask import Flask, render_template, Response, send_from_directory
from flask_socketio import SocketIO
import cv2

from camera import Camera
cam = Camera()
time.sleep(1)

from detector import Detector
det = Detector()

from motor import Motor
 
m2 = Motor("/dev/serial/by-id/usb-Raspberry_Pi_Pico_504450612038C51C-if00")
m1 = Motor("/dev/serial/by-id/usb-Waveshare_RP2040_Zero_504450612862EA1C-if00")

# web server
app = Flask(__name__)
socketio = SocketIO(app)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# %%
scale = 0.415
f = cam()
dg = det(f)
p = 0.1
threshold = 1e-2
last = time.time()

pos = np.array([pi, pi])
m1(pos[0])
m2(pos[1])
time.sleep(0.2)
# overpower the axis to be perpendicular


def loop():
    global f, dg, p, pos, last
    f = cam()
    d = det(f)
    tracking = False
    if d["signal"] > threshold:
        tracking = True
        error = (d["center"]-np.array([0.5, 0.5]))*scale*[4/3, 1]
        pos[0] += p*error[0]
        m1(pos[0])
        pos[1] -= p*error[1] * - cos(pos[0])
        m2(pos[1])
    td = time.time() - last
    last = time.time()
    dg = {
        **d,
        "threshold": threshold,
        "tracking": tracking,
        "time": td
    }
    socketio.emit("data", json.dumps(dg))

loop()

from threading import Thread
running = True
def tracking_task():
    global running
    while running:
        loop()

# %%
tracking = Thread(target=tracking_task)
tracking.start()

# %%
# https://github.com/log0/video_streaming_with_flask_example
def gen():
    global f
    while True:
        ret, buf = cv2.imencode(".jpg", f[...,::-1])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n\r\n')
        time.sleep(1/30)

@app.route('/')
def index():
        return send_from_directory('static/', "index.html")

@app.route('/<path:path>')
def sendstuff(path):
    return send_from_directory('static/', path, max_age=0)

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on("setting")
def on_setting(data):
    global threshold
    data = json.loads(data)
    print(data)
    if "threshold" in data:
        threshold = float(data["threshold"])

socketio.run(app, host='0.0.0.0', port=8080)
# %%