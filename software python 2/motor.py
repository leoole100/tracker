#%%
import serial, math

class Motor():
	def __init__(self):
		self.ser = serial.Serial('/dev/ttyACM0')

	# 250 us
	def __call__(self, a:float):
		if(a>=0 and a<=2*math.pi):
			self.ser.write(b'T'+bytes(f"{a:f}", "ascii")+b'\n')
			return True
		return False

	def __del__(self):
		self.ser.close()
