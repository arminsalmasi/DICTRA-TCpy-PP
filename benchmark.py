import time
import numpy as np

data = [np.random.rand(100, 2) for _ in range(1000)]

def baseline_get_xlims(data):
    if not data:
        raise ValueError("empty data")
    return [np.min([d[:, 0].min() for d in data]), np.max([d[:, 0].max() for d in data])]

start = time.perf_counter()
for _ in range(100):
    baseline_get_xlims(data)
baseline_time = time.perf_counter() - start
print("Baseline:", baseline_time)

def optimized_get_xlims(data):
    if not data:
        raise ValueError("empty data")
    return [min(d[:, 0].min() for d in data), max(d[:, 0].max() for d in data)]

start = time.perf_counter()
for _ in range(100):
    optimized_get_xlims(data)
optimized_time = time.perf_counter() - start
print("Optimized:", optimized_time)
print(f"Improvement: {(baseline_time - optimized_time) / baseline_time * 100:.2f}%")
