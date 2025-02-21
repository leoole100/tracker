#%%

using ZMQ
using Images
using ImageIO
using JSON
using StringEncodings
using Base64
using JpegTurbo

# connect to sub
ctx = Context()
sub = Socket(ctx, SUB)
pub = Socket(ctx, PUB)
connect(sub, "tcp://127.0.0.1:5555")
connect(pub, "tcp://127.0.0.1:5556")

subscribe(sub, "camera_frame")

frame = recv(sub)
# get the first frame
#%%
json_str = split(String(frame), " ", limit=2)[2]
json_obj = JSON.parse(json_str)
jpg_str = json_obj["image"]
jpg_bytes = base64decode(jpg_str)
img = jpeg_decode(jpg_bytes)

# %%

# detect color
img_lab = Lab.(img)
color = Lab{Float32}(69.42, 149.31, 156.84)

function center_of_mass(img_lab::Array{Lab{Float32},2}, color::Lab{Float32})
	cent1 = 0.0
	cent2 = 0.0
	weight = 0.0
	color_a, color_b = color.a, color.b
	c = color
	@inbounds for x in 1:size(img_lab, 1)
		@inbounds for y in 1:size(img_lab, 2)
			c =  img_lab[x, y]
			# w = - exp((color_a - c.a)^2 + (color_b - c.b)^2/(2 * 10^2))
			w = (color_a - c.a)^2 + (color_b - c.b)^2
			cent1 += Float32(x) * w
			cent2 += Float32(y) * w
			weight += w
		end
	end
	return [cent1 / weight, cent2 / weight]
end

using Profile
using BenchmarkTools
center_of_mass(img_lab)
@timed center_of_mass(img_lab)
@profview center_of_mass(img_lab);