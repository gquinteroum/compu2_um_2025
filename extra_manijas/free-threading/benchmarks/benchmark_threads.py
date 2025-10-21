import threading
import time
import math
import sys

# ============================================
# CPU-bound task: heavy math loop
# ============================================
def heavy_computation(n):
    total = 0.0
    for i in range(1, n):
        total += math.sqrt(i) * math.sin(i) * math.cos(i/2)
    return total

def run_test(num_threads: int, n: int):
    start = time.perf_counter()
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=heavy_computation, args=(n,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start
    print(f"{num_threads:2d} threads -> {elapsed:6.2f} s")

# ============================================
# Entry point
# ============================================
if __name__ == "__main__":
    print(f"Python version: {sys.version.split()[0]}")
    try:
        print(f"GIL enabled: {sys._is_gil_enabled()}")
    except AttributeError:
        print("sys._is_gil_enabled() not available in this build")

    print("\nRunning CPU-bound benchmark...\n")

    for threads in [1, 2, 4, 8]:
        run_test(threads, 10_000_000)
