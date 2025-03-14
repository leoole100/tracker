# %%
import time
def measure_fps(f:callable, N=100):
    start = time.time()
    for i in range(N):
        f()
    t = time.time() - start
    print(f"{t/N * 1000 : .3g} ms, {N/t : .3g} Hz")
