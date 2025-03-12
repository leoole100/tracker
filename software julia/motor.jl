using LibSerialPort

sp = LibSerialPort.open("/dev/ttyACM0", 115200)

function setAngle(a::Number)
	a = clamp(a, 0, 2pi)
	write(sp,"T"*string(a)*"\n")
end