cd(@__DIR__)
include("detector.jl") # also starts the camera
include("motor.jl")

# @btime find_center(read_frame()) # 120 Hz
read_frame()

# %%
Threshold_low = 7.
Threshold_heigh = Threshold_low*1.2
P = 0.3
Scale = 0.415
a = pi
tracking = false

setAngle(a)

function loop()
	global a, tracking
	c, s = find_center(read_frame())
	print(s)
	print("\t")
	print(a)
	
	if (tracking && s > Threshold_low) || (!tracking && s>Threshold_heigh)
		error = c[1] / size(f_small, 1) - 0.5
		a += error*Scale*P
		setAngle(a)
		print("\t")
		print(error)
		tracking = true
	else
		tracking = false
	end
	println()
end

function run()
	while true
		loop()
	end	
end

println("starting")
run()