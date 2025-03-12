cd(@__DIR__)
include("camera.jl")
using ImageIO, FFTW

start_camera()

# %%

# get a image
f = read_frame()

#%%
# get the color of the ball
template = load("../ball.png")
template_hsv = channelview(HSV.(template)) ./ [360, 1, 1]
hsv_mean = [mean(template_hsv[i,:,:]) for i in range(1,3)]
hsv_var = [std(template_hsv[i,:,:]) for i in range(1,3)]

# allocate memory
f_small = imresize(f, (120, 160))
f_hsv = channelview(HSV.(f_small)) ./ [360, 1, 1]
diff_hsv = f_hsv.-hsv_mean
w = mean(diff_hsv.^2 ./ hsv_var, dims=1)[1, :, :]
krn =  Kernel.gaussian(1)

function find_center(f)
	f_small = imresize(f, (120, 160))
	f_hsv .= channelview(HSV.(f_small)) ./ [360, 1, 1]
	diff_hsv .= f_hsv.-hsv_mean
	w .= -mean(diff_hsv.^2 ./ hsv_var, dims=1)[1, :, :]
	w .= exp.(w)
	# w .= ImageFiltering.imfilter(w, krn)
	amax = argmax(w)
	snr = w[amax] / mean(w)
	return amax, snr
end

print(find_center(f))
mosaic(Gray.(w/maximum(w)))


# @btime find_center(f);
