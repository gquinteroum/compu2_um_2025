from multiprocessing import Pool
import os
import time

def f(x):
    time.sleep(100)
    return x*x, os.getpid()
#    return x*x

print(os.getpid())
with Pool(processes=4) as pool:
    x = range(10)
    print(list(x))
    input()
    print(pool.map(f, range(10)))

