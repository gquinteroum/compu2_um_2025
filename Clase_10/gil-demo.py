import threading
import multiprocessing
import time
import os

def fix_cpu(cpu_id):
    try:
        os.sched_setaffinity(0, {cpu_id})
    except AttributeError:
        pass  # No disponible en Windows o Mac

def compute_atomic(name, count=500_000, cpu_id=None):
    if cpu_id is not None:
        fix_cpu(cpu_id)

    pid = os.getpid()
    print(f"{name} started on PID {pid}")
    
    x = 0
    start = time.time()
    for _ in range(count):
        x += 1  # Operación atómica (protegida por el GIL en threads)
    end = time.time()

    print(f"{name} finished in {end - start:.2f} sec (PID {pid})")

def run_threads():
    print("\n[THREADING]")
    t1 = threading.Thread(target=compute_atomic, args=("Thread A",))
    t2 = threading.Thread(target=compute_atomic, args=("Thread B",))
    start = time.time()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f"Total time (threading): {time.time() - start:.2f} sec")

def run_processes():
    print("\n[MULTIPROCESSING]")
    p1 = multiprocessing.Process(target=compute_atomic, args=("Process A", 500_000_000, 0))
    p2 = multiprocessing.Process(target=compute_atomic, args=("Process B", 500_000_000, 1))
    start = time.time()
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(f"Total time (multiprocessing): {time.time() - start:.2f} sec")

if __name__ == '__main__':
    run_threads()
    time.sleep(2)
    run_processes()

