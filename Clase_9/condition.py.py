import threading
import time

condition = threading.Condition()
shared_data = []

def consumer():
    print("[CONSUMER] Arranca")
    with condition:
        print("[CONSUMER] Tiene el lock")
        while not shared_data:
            print("[CONSUMER] shared_data vacío. Va a esperar...")
            condition.wait()
            print("[CONSUMER] Despertó y tiene de nuevo el lock")
        data = shared_data.pop(0)
        print(f"[CONSUMER] Consumió el dato: {data}")
    print("[CONSUMER] Fuera del with (lock liberado)")

def producer():
    print("[PRODUCER] Arranca")
    time.sleep(1)
    with condition:
        print("[PRODUCER] Tiene el lock")
        shared_data.append("¡Dato listo!")
        print("[PRODUCER] Dato agregado. Llama a notify()")
        condition.notify()
        print("[PRODUCER] notify() hecho, aún dentro del with")
        time.sleep(2)
        print("[PRODUCER] Va a salir del with y liberar el lock")
    print("[PRODUCER] Fuera del with (lock liberado)")

t1 = threading.Thread(target=consumer)
t2 = threading.Thread(target=producer)

t1.start()
t2.start()

t1.join()
t2.join()

