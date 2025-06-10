import time
from threading import Thread
from multiprocessing import Process

# Número de tareas concurrentes a lanzar
N = 100

def dummy_task():
    """Tarea mínima sin operación real, para medir solo el costo de coordinación."""
    pass

def run_threads():
    """Ejecuta N hilos que hacen dummy_task"""
    threads = [Thread(target=dummy_task) for _ in range(N)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def run_processes():
    """Ejecuta N procesos que hacen dummy_task"""
    processes = [Process(target=dummy_task) for _ in range(N)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

if __name__ == '__main__':
    # Mide el tiempo de ejecución con threads
    start = time.time()
    run_threads()
    print(f"Threading overhead: {time.time() - start:.6f} sec")

    # Mide el tiempo de ejecución con procesos
    start = time.time()
    run_processes()
    print(f"Multiprocessing overhead: {time.time() - start:.6f} sec")

