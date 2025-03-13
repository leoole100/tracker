#%%
from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from threading import Thread
from multiprocessing import Queue, Process

# %%
app = Flask(__name__)

# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

socketio = SocketIO(app)


@app.route('/')
def index():
        return send_from_directory('static/', "index.html")

@app.route('/<path:path>')
def sendstuff(path):
    return send_from_directory('static/', path, max_age=0)

# %%

def tracker(q: Queue):
    import tracker
    while True:
        tracker.loop()
        if not q.full():
            q.put(tracker.f)

def send_frames(q: Queue):
    import cv2, base64, time
    while True:
        f = q.get()
        ret, buffer = cv2.imencode('.jpg', f[...,::-1])
        socketio.emit("frame",base64.b64encode(buffer).decode('utf-8'))
        time.sleep(0.1)

def server():
    # Run the Flask application with SocketIO
    socketio.run(app, host='0.0.0.0', port=8080)

# %%
    
try:
    frames = Queue(2)

    print("starting send frames")
    sub_thread = Thread(target=send_frames, name="send frames", args=(frames,))
    sub_thread.start()

    print("starting tracker")
    tracker_process = Process(target=tracker, args=(frames,), name="tracker")
    tracker_process.start()
    
    print("starting server")
    server_thread = Thread(target=server, name="server")
    server_thread.start()


except:
    tracker_process.kill()

# %%
