## Marco Teórico Profundo sobre Procesos y Programación Concurrente en Python

---

### 1. Fundamentos de Procesos y Programación Concurrente

#### ¿Qué es un proceso?

Un **proceso** es una instancia de un programa en ejecución. No se trata solo del código ejecutable, sino de todo su **contexto de ejecución**: memoria asignada, descriptores de archivos abiertos, pila de ejecución, registros de CPU, entorno de variables, entre otros. Cada proceso en un sistema operativo moderno es aislado: posee su propio espacio de direcciones, lo cual garantiza que no pueda acceder directamente a la memoria de otros procesos, favoreciendo la estabilidad y seguridad del sistema.

#### Hilos vs. Procesos

Los **hilos** (o threads) son unidades más livianas de ejecución dentro de un proceso. Comparten el mismo espacio de memoria y recursos del proceso padre, lo que permite una comunicación rápida entre ellos, pero también introduce **riesgos de concurrencia**, como condiciones de carrera o corrupción de memoria compartida.

| Característica      | Proceso                          | Hilo                                   |
| ------------------- | -------------------------------- | -------------------------------------- |
| Memoria             | Aislada entre procesos           | Compartida entre hilos                 |
| Creación            | Costosa                          | Más liviana                            |
| Comunicación        | Requiere IPC (pipes, sockets...) | Directa mediante variables compartidas |
| Tolerancia a fallos | Alta (aislamiento)               | Baja (un error puede colapsar todo)    |

---

### 2. Multiprocessing en Python: Ventajas y Desventajas

Python posee un Global Interpreter Lock (**GIL**) que impide la ejecución concurrente real de múltiples hilos en un mismo proceso en arquitecturas multi-core. Esto afecta negativamente los programas CPU-bound.

La biblioteca `multiprocessing` permite sortear esta limitación ejecutando procesos independientes en paralelo, aprovechando múltiples núcleos.

#### Ventajas:

* Evita el GIL, permitiendo verdadero paralelismo.
* Cada proceso tiene su propio espacio de memoria: menos riesgo de corrupción.
* Mayor robustez frente a fallos: un proceso colapsado no afecta a los demás.

#### Desventajas:

* La comunicación entre procesos es más costosa (requiere mecanismos como Pipes o Queues).
* Mayor consumo de recursos que los hilos.
* Serialización necesaria para compartir datos.

---

### 3. Creación y Gestión de Procesos Básicos

La clase `multiprocessing.Process` encapsula un proceso nuevo. Un ejemplo mínimo:

```python
from multiprocessing import Process

def saludo():
    print("Hola desde otro proceso")

if __name__ == '__main__':
    p = Process(target=saludo)
    p.start()
    p.join()
```

#### Métodos principales:

* `start()`: lanza el proceso.
* `join()`: espera a que termine.
* `is_alive()`: verifica si sigue ejecutándose.

#### Ciclo de vida:

1. Creación del objeto `Process`.
2. Inicio (`start`) → Proceso hijo nace con su propia memoria.
3. Ejecución concurrente.
4. Finalización y recolección de recursos.

#### Identificación y jerarquía:

Cada proceso tiene un `pid` y puede conocer el `ppid` (pid del padre). Esto permite construir árboles de procesos y manejar relaciones entre padres e hijos.

---

### 4. Comunicación Entre Procesos Básica (IPC)

#### Pipes

Los `Pipe()` crean dos extremos conectados:

```python
from multiprocessing import Pipe

parent_conn, child_conn = Pipe()
parent_conn.send("hola")
print(child_conn.recv())
```

* Ideal para comunicación bidireccional entre dos procesos.
* Rápido pero limitado a dos extremos.

#### Queues

Basado en `queue.Queue`, pero adaptado a procesos. Internamente usa un Pipe y Lock para garantizar sincronización.

```python
from multiprocessing import Queue

q = Queue()
q.put("dato")
print(q.get())
```

* Permite múltiples productores y consumidores.
* Seguro para concurrencia.

#### Comparación:

* **Pipes**: simples, rápidos, para 2 procesos.
* **Queues**: escalables, seguros, pero con mayor overhead.

---

### 5. Sincronización Básica

#### Condiciones de carrera

Ocurren cuando varios procesos acceden y modifican simultáneamente una misma variable compartida, generando resultados impredecibles.

#### Locks

Se usan para proteger secciones críticas:

```python
from multiprocessing import Lock

lock = Lock()

with lock:
    # zona crítica segura
```

Evitan que más de un proceso ejecute código crítico al mismo tiempo.

---

### 6. Ejercicio Práctico: mp\_worker.py

Modificar el archivo `mp_worker.py` para incluir varias instancias de `Process` ejecutando tareas CPU-bound en paralelo. Medir el tiempo total y comparar con la versión secuencial para demostrar el uso real de varios núcleos.

---

### Conclusiones

* Python limita el uso de hilos para tareas CPU-bound debido al GIL, pero `multiprocessing` lo supera con procesos independientes.
* Pipes y Queues ofrecen mecanismos prácticos de comunicación, con distintas ventajas según el escenario.
* La sincronización con Locks es esencial para evitar condiciones de carrera.

---

### Referencias

* Python `multiprocessing` docs: [https://docs.python.org/3/library/multiprocessing.html](https://docs.python.org/3/library/multiprocessing.html)
* Tanenbaum, A. S. "Modern Operating Systems"
* The Little Book of Semaphores - Allen B. Downey

---
