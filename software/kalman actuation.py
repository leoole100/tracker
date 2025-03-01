import serial
import zmq
import json
import cv2
import base64
import numpy as np
import time
import math
from threading import Thread
from queue import Queue

ser = serial.Serial('/dev/ttyACM0')

getAngle = lambda: float(ser.readline()) # 200 us
# setAngle = lambda a: ser.write(b'T'+bytes(f"{a:f}", "ascii")+b'\n') # 300us
def setAngle(a):
    if(a>0 and a<2*math.pi):
        ser.write(b'T'+bytes(f"{a:f}", "ascii")+b'\n')

rad_frame = 0.541 * np.array([16/9, 1])

measurements = Queue(1)

def recieve_mesurements():
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://localhost:5556") # detector
    sub.setsockopt_string(zmq.SUBSCRIBE, "detection")
    sub.setsockopt(zmq.CONFLATE, 1) # take most recent
 
    while True:
        message = sub.recv_string()
        topic, data = message.split(" ", 1)

        data = json.loads(data)

        if data["valid"]:
            measurements.put(data)
   
def main():
    kalman = cv2.KalmanFilter(4, 2)
    kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
    kalman.transitionMatrix = np.array([
        [1, 0, 1, 0],  # x = x + vx*dt
        [0, 1, 0, 1],  # y = y + vy*dt
        [0, 0, 1, 0],  # vx = vx
        [0, 0, 0, 1]   # vy = vy
    ], np.float32)
    kalman.processNoiseCov = 1e-4 * np.eye(4, dtype=np.float32)  # Tune this
    kalman.measurementNoiseCov = 1e-2 * np.eye(2, dtype=np.float32)  # Tune this

    # Initialize with first detection
    current_measurement = np.array([[0.5], [0.5]], dtype=np.float32)
    kalman.statePost = np.array([[0.5], [0.5], [0], [0]], dtype=np.float32)

    a = math.pi
    last_time = 0    
    last_position = a
    setAngle(a)
    
    while True:
        if not measurements.empty():
            c = measurements.get()["center"]
            current_measurement = np.array([[c[0]], [c[1]]], dtype=np.float32)
            if last_time-time.time() > 0.5:
                kalman.statePost = current_measurement
            else:
                kalman.correct(current_measurement)
            last_time = time.time()
            last_postion = a
        
        predicted_state = kalman.predict()
        x_pred, y_pred = predicted_state[0], predicted_state[1]
        
        a += (predicted_state[1, 0]-0.5)*rad_frame[1] *15* 1/100 /2
        if time.time()-last_time > 0.5:
            a = last_position

        setAngle(a)
        
        time.sleep(1/100)
    
if __name__ == "__main__":
    thread = Thread(target = recieve_mesurements)
    thread.start()
    main()