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

def send_messages():
    import zmq
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://lab.local:5001")
    sub.connect("tcp://lab.local:5002")
    sub.setsockopt_string(zmq.SUBSCRIBE, "")
    
    try:
        while True:
            # Wait for a message from the publisher
            message = sub.recv_string()
            try:
                    topic, data = message.split(" ", 1)
            except ValueError:
                    continue  # Skip if message format is not as expected
            
            # Emit the frame to all connected web clients via SocketIO
            socketio.emit(topic, data)

    finally:
        sub.close()
        context.term()

def server():
    # Run the Flask application with SocketIO
    socketio.run(app, host='0.0.0.0', port=8080)

# %%    
print("starting send frames")
sub_thread = Thread(target=send_messages, name="ws")
sub_thread.start()

print("starting server")
server_thread = Thread(target=server, name="server")
server_thread.start()

# %%
