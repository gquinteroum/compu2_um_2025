import math
import time
from threading import Thread
from multiprocessing import Process, cpu_count

def is_prime(n):
    """Verifica si un número es primo"""
    if n < 2: return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0: return False
    return True

def count_primes_in_range(start, end):
    """Cuenta los primos en el rango [start, end)"""
    count = 0
    for i in range(start, end):
        if is_prime(i):
            count += 1

def run_in_threads():
    """Distribuye la carga en hilos (no se beneficia del paralelismo real por el GIL)"""
    threads = []
    for i in range(cpu_count()):
        t = Thread(target=count_primes_in_range, args=(i*10000, (i+1)*10000))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

def run_in_processes():
    """Distribuye la carga en procesos (paralelismo real, evita el GIL)"""
    processes = []
    for i in range(cpu_count()):
        p = Process(target=count_primes_in_range, args=(i*10000, (i+1)*10000))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()

if __name__ == '__main__':
    print("=== CPU Bound ===")
    start = time.time()
    run_in_threads()
    print(f"Threading: {time.time() - start:.2f} sec")

    start = time.time()
    run_in_processes()
    print(f"Multiprocessing: {time.time() - start:.2f} sec")

