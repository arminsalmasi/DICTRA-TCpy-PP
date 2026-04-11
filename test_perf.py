import numpy as np
import time

def calculate_u_fractions_original(mf, sub_idx, elnames):
    sub_sum = np.sum(mf[:, sub_idx], axis=1)
    sub_sum[sub_sum == 0] = 1.0
    uf = []
    for nel, el in enumerate(elnames):
        uf.append(mf[:, nel] / sub_sum[:])
    return np.array(uf)

def calculate_u_fractions_optimized(mf, sub_idx, elnames):
    sub_sum = np.sum(mf[:, sub_idx], axis=1)
    sub_sum[sub_sum == 0] = 1.0
    return (mf / sub_sum[:, np.newaxis]).T

M = 1000000
N = 10
mf = np.random.rand(M, N)
sub_idx = [0, 1, 2, 3]
elnames = np.array(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])

# Warm up
calculate_u_fractions_original(mf, sub_idx, elnames)
calculate_u_fractions_optimized(mf, sub_idx, elnames)

t0 = time.time()
orig = calculate_u_fractions_original(mf, sub_idx, elnames)
t1 = time.time()
print(f"Original: {t1-t0:.4f}s")

t0 = time.time()
opt = calculate_u_fractions_optimized(mf, sub_idx, elnames)
t1 = time.time()
print(f"Optimized: {t1-t0:.4f}s")

print(f"Same output? {np.allclose(orig, opt)}")
