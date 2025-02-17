import cv2
import zmq
import base64
import signal

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
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    try:
        while running:
            ret, frame = cap.read()
            if not ret:
                continue

            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            # Optionally encode JPEG bytes to a base64 string (if needed)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')

            # Publish the frame with a topic prefix
            socket.send_string("camera_frame " + jpg_as_text)

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
