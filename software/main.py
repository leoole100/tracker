
# %%
from multiprocessing import Queue, Process

def tracker(q: Queue):
    import tracker
    while True:
        tracker.loop()
        if not q.full():
            q.put(tracker.f)

def send_frames(q: Queue):
    import cv2, base64, zmq
    context = zmq.Context()
    pub = context.socket(zmq.PUB)
    pub.bind("tcp://*:5001")
        
    while True:
        try:
            f = q.get()
            ret, buffer = cv2.imencode('.jpg', f[...,::-1])
            pub.send_string("frame " + base64.b64encode(buffer).decode('utf-8'))
        except: break
    
    context.term()

def send_tracking(q: Queue):
    import zmq, json
    context = zmq.Context()
    pub = context.socket(zmq.PUB)
    pub.bind("tcp://*:5002")
        
    while True:
        try:
            t = q.get()
            pub.send_string("track " + json.dumps(t))
        except: break
    
    context.term()
        
def tracker(fq: Queue, tq: Queue):
    import tracker
    t = None
    while True:
        t = tracker.loop()
        if not fq.full(): fq.put(tracker.f)
        if not tq.full(): tq.put(t)
            
#%%
frames = Queue(2)
tracking = Queue(2)

print("starting send frames")
encoder_task = Process(target=send_frames, name="send frames", args=(frames,))
encoder_task.start()

print("starting send tracker")
telemetry_task = Process(target=send_tracking, args=(tracking,), name="telemetry")
telemetry_task.start()

print("starting tracker")
tracker_task = Process(target=tracker, args=(frames, tracking, ), name="tracker")
tracker_task.start()



# %%
try:
    tracker_task.join()    
except:
    encoder_task.kill()
    telemetry_task.kill()
    tracker_task.kill()