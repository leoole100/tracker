#=
gives a 20ms delayed frame with a maximum speed of 100 Hz
=#

using PyCall
using BenchmarkTools
using Images
using Profile

function start_camera(fps::Number = 200)
    py"""
    from picamera2 import Picamera2

    c = Picamera2()
    conf = 	c.create_preview_configuration(
        queue=False,
        buffer_count=2
    )
    c.start(conf)

    def set_fps(fps:float):
        c.set_controls({"FrameRate": fps})

    def read_frame(c:Picamera2 = c):
        return c.capture_array()[...,:3]
    """
    py"set_fps"(fps)
end

function read_frame()
    frame = py"read_frame()"
    return reinterpretc(RGB{N0f8}, permutedims(frame, (3, 1, 2)))
end

function measure_fps(N=100)
    frame = read_frame()
    start = time()
    for i in range(1, N)
        frame = read_frame()
    end
    return N/(time()-start)
end

function close_camera()
    py"""
    c.stop() 
    c.close()
    """
end