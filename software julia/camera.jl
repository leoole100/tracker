#=
gives a 20ms delayed frame with a maximum speed of 100 Hz
=#

using PyCall
using BenchmarkTools
using Images
using Profile

function Camera(fps::Number = 200)
    picam = pyimport("picamera2")
    c = picam.Picamera2()
    conf = 	c.create_preview_configuration(queue=false,buffer_count=2)
    c.start(conf)
    c.set_controls(Dict("FrameRate"=>fps))
    return c
end

function read_frame(c)
    frame = c.capture_array()
    frame = frame[:,:,1:3]
    return reinterpretc(RGB{N0f8}, permutedims(frame, (3, 1, 2)))
end

function read_frame!(c, frame)
    frame = c.capture_array()
    frame = frame[:,:,1:3]
    return frame = reinterpretc(RGB{N0f8}, permutedims(frame, (3, 1, 2)))
end

function measure_fps(c, N=100)
    frame = read_frame()
    start = time()
    for i in range(1, N)
        frame = read_frame()
    end
    return N/(time()-start)
end

function close(c)
    c.stop()
    c.close() 
end