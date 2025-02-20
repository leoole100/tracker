from camera import setup_camera
import time
N = 100

cap = setup_camera()

for i in range(5):
	ret, frame = cap.read()

start = time.time()
for i in range(N):
	ret, frame = cap.read()
	if not ret:
		continue
end = time.time()
print(f"Framerate: {N / (end - start):.2f} FPS")
cap.release()