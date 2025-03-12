cd(@__DIR__)
include("detector.jl") # also starts the camera
include("motor.jl")

# @btime find_center(read_frame()) # 120 Hz
read_frame()

# %%
Threshold = 25
Scale = 0.415
a = pi
P = 0.2

setAngle(a)

function loop()
	global a
	c, s = find_center(read_frame())
	print(s)
	print("\t")
	print(a)
	if s > Threshold
		error = c[1] / size(f_small, 1) - 0.5
		a += error*Scale*P
		setAngle(a)
		print("\t")
		print(error)
	end
	println()
end

function run()
	while true
		loop()
	end	
end
