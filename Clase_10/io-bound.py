import time
from threading import Thread
from multiprocessing import Process

# Número de tareas
N = 300

def io_task():
    """Simula una operación bloqueante de I/O (como leer de red o disco)"""
    time.sleep(0.3)

def run_io_threads():
    """Ejecuta N tareas I/O usando hilos"""
    threads = [Thread(target=io_task) for _ in range(N)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def run_io_processes():
    """Ejecuta N tareas I/O usando procesos"""
    processes = [Process(target=io_task) for _ in range(N)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

if __name__ == '__main__':
    print("=== IO Bound ===")
    start = time.time()
    run_io_threads()
    print(f"Threading (I/O): {time.time() - start:.2f} sec")

    start = time.time()
    run_io_processes()
    print(f"Multiprocessing (I/O): {time.time() - start:.2f} sec")

