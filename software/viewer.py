import zmq
import threading
import base64
from flask import Flask, render_template, send_from_directory, send_file
from flask_socketio import SocketIO

app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


socketio = SocketIO(app)


def main():
	context = zmq.Context()
	sub = context.socket(zmq.SUB)
	sub.connect("tcp://localhost:5555")
	sub.connect("tcp://localhost:5556")
	sub.setsockopt_string(zmq.SUBSCRIBE, "")
	sub.setsockopt(zmq.CONFLATE, 1) # take most recent

	pub = context.socket(zmq.PUB)
	pub.bind("tcp://*:5550")

	@socketio.on("message")
	def on_message(data):
		print(data)
		pub.send_string(data)

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
