import zmq
import threading
import base64
from flask import Flask, render_template, send_from_directory, send_file
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

def main():
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect("tcp://localhost:5555")
	socket.connect("tcp://localhost:5556")
	socket.setsockopt_string(zmq.SUBSCRIBE, "")

	socketio.on_event('message', lambda data: socket.send_string(data))
	
	try:
		while True:
			# Wait for a message from the publisher
			message = socket.recv_string()
			try:
					topic, data = message.split(" ", 1)
			except ValueError:
					continue  # Skip if message format is not as expected
			
			# Emit the frame to all connected web clients via SocketIO
			socketio.emit(topic, data)

	finally:
		socket.close()
		context.term()

@app.route('/')
def index():
		return send_from_directory('static/', "index.html")

@app.route('/<path:path>')
def sendstuff(path):
	return send_from_directory('static/', path, max_age=0)

if __name__ == '__main__':
		# Start the ZeroMQ subscriber in a background thread
		sub_thread = threading.Thread(target=main, name="zmq to socketio")
		sub_thread.daemon = True
		sub_thread.start()

		# Run the Flask application with SocketIO
		socketio.run(app, host='0.0.0.0', port=8080)
