import cv2
import zmq
import base64
import signal
import time
import json

# Global flag to control the main loop
running = True

def signal_handler(sig, frame):
		global running
		print("Shutdown signal received. Exiting gracefully...")
		running = False

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
		global running

		# Set up ZeroMQ publisher
		context = zmq.Context()
		socket = context.socket(zmq.PUB)
		socket.bind("tcp://*:5555")  # Bind to port 5555

		# Open the camera (usually device 0)
		cap = cv2.VideoCapture(0)

		# Set camera properties
		assert cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
		assert cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
		assert cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
		assert cap.set(cv2.CAP_PROP_FPS, 30)
		assert cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Set codec to MJPG for compression

		if not cap.isOpened():
				print("Error: Cannot open camera")
				return

		try:
				while running:
						ret, frame = cap.read()
						frame_time = time.time()
						if not ret:
								continue

						# Encode the frame as JPEG
						ret, buffer = cv2.imencode('.jpg', frame)
						if not ret:
								continue

						# Optionally encode JPEG bytes to a base64 string (if needed)
						jpg_as_text = base64.b64encode(buffer).decode('utf-8')
						
						encoding_time = time.time()
						
						# create a json dict with times and data
						data = {
							"time": frame_time,
							"times": {
								"encoding": encoding_time - frame_time,
							},
							"image": jpg_as_text,
						}

						# Publish the frame with a topic prefix
						socket.send_string("camera_frame " + json.dumps(data))

		except KeyboardInterrupt:
				print("KeyboardInterrupt caught, shutting down...")

		finally:
				# Cleanup resources
				cap.release()
				socket.close()
				context.term()
				print("Shutdown complete.")

if __name__ == '__main__':
		main()
