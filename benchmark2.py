import time
import numpy as np
import sys

data = [np.random.rand(10, 2) for _ in range(100000)] # Many smaller arrays

def baseline_get_xlims(data):
    if not data:
        raise ValueError("empty data")
    return [np.min([d[:, 0].min() for d in data]), np.max([d[:, 0].max() for d in data])]

def optimized_get_xlims(data):
    if not data:
        raise ValueError("empty data")
    return [min(d[:, 0].min() for d in data), max(d[:, 0].max() for d in data)]

import tracemalloc
tracemalloc.start()
baseline_get_xlims(data)
base_mem = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()

tracemalloc.start()
optimized_get_xlims(data)
opt_mem = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()

print(f"Baseline Peak Memory: {base_mem / 1024:.2f} KB")
print(f"Optimized Peak Memory: {opt_mem / 1024:.2f} KB")


start = time.perf_counter()
for _ in range(10):
    baseline_get_xlims(data)
baseline_time = time.perf_counter() - start
print("Baseline Time:", baseline_time)

start = time.perf_counter()
for _ in range(10):
    optimized_get_xlims(data)
optimized_time = time.perf_counter() - start
print("Optimized Time:", optimized_time)
print(f"Improvement Time: {(baseline_time - optimized_time) / baseline_time * 100:.2f}%")
