import time
import numpy as np
import tracemalloc

# Create a scenario simulating large simulation outputs (e.g. 5000 arrays of ~1000 points)
data = [np.random.rand(1000, 2) for _ in range(5000)]

def baseline_get_xlims(data):
    if not data:
        raise ValueError("empty data")
    return [np.min([d[:, 0].min() for d in data]), np.max([d[:, 0].max() for d in data])]

def optimized_get_xlims(data):
    if not data:
        raise ValueError("empty data")
    return [min(d[:, 0].min() for d in data), max(d[:, 0].max() for d in data)]

# Warmup
baseline_get_xlims(data)
optimized_get_xlims(data)

# Baseline Memory
tracemalloc.start()
baseline_get_xlims(data)
base_mem, base_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

# Optimized Memory
tracemalloc.start()
optimized_get_xlims(data)
opt_mem, opt_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Baseline Peak Memory: {base_peak / 1024:.2f} KB")
print(f"Optimized Peak Memory: {opt_peak / 1024:.2f} KB")
print(f"Memory Savings: {(base_peak - opt_peak) / base_peak * 100:.2f}%")

# Baseline Time
start = time.perf_counter()
for _ in range(20):
    baseline_get_xlims(data)
baseline_time = time.perf_counter() - start

# Optimized Time
start = time.perf_counter()
for _ in range(20):
    optimized_get_xlims(data)
optimized_time = time.perf_counter() - start

print(f"Baseline Time: {baseline_time:.4f}s")
print(f"Optimized Time: {optimized_time:.4f}s")
print(f"Time Improvement: {(baseline_time - optimized_time) / baseline_time * 100:.2f}%")
