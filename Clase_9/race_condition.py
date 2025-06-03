from multiprocessing import Process, Value
import time
import ctypes

def unsafe_increment(counter):
    for _ in range(10000):
        temp = counter.value
        #time.sleep(0.0003) 
        counter.value = temp + 1

if __name__ == '__main__':
    shared_counter = Value(ctypes.c_int, 0)

    p1 = Process(target=unsafe_increment, args=(shared_counter,))
    p2 = Process(target=unsafe_increment, args=(shared_counter,))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print(f"Valor final: {shared_counter.value}")  # Probablemente < 20000

