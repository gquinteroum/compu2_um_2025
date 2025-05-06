## Serie Progresiva de Ejercicios sobre Procesos y Concurrencia en Python

A continuación se presentan **diez ejercicios** ordenados por dificultad. Los cinco primeros incluyen una solución detallada; los cinco restantes quedan como desafío.

---

### Parte I · Ejercicios Resueltos

#### Ejercicio 1 · Nivel Básico

> **Objetivo**: comprobar la creación de procesos y la correcta espera del padre.
>
> **Enunciado**: escribe un programa que cree dos procesos hijo mediante `multiprocessing.Process`, cada uno imprimiendo su propio `pid`. El proceso padre debe esperar a que ambos terminen y luego imprimir un mensaje de cierre.

**Solución comentada**:

```python
from multiprocessing import Process, current_process

def hijo():
    print(f"[Hijo] PID: {current_process().pid}")

if __name__ == '__main__':
    procesos = [Process(target=hijo) for _ in range(2)]
    for p in procesos:
        p.start()
    for p in procesos:
        p.join()
    print('[Padre] Hijos finalizados — PID padre:', current_process().pid)
```

*Comentario*: se ilustra el ciclo `start() → join()` y la diferenciación de PIDs.

---

#### Ejercicio 2 · Nivel Intermedio

> **Objetivo**: usar `Queue` para reunir resultados de varios procesos.
>
> **Enunciado**: implementa un script que genere $n = 4$ procesos; cada proceso calcula la suma de los primeros $k = 1\,000\,000$ enteros y deposita el resultado en una `Queue`. El padre recoge los cuatro resultados y verifica que sean idénticos.

**Solución resumida**:

```python
from multiprocessing import Process, Queue

def worker(k, q):
    q.put(sum(range(k)))

if __name__ == '__main__':
    k = 1_000_000
    q = Queue()
    ps = [Process(target=worker, args=(k, q)) for _ in range(4)]
    for p in ps: p.start()
    resultados = [q.get() for _ in ps]
    for p in ps: p.join()
    assert len(set(resultados)) == 1
    print('Todos iguales:', resultados[0])
```

*Comentario*: se observa comunicación **many‑to‑one** y verificación de integridad.

---

#### Ejercicio 3 · Nivel Intermedio +

> **Objetivo**: demostrar una condición de carrera y su corrección con `Lock`.
>
> **Enunciado**: crea un contador global al que dos procesos suman 1, cincuenta mil veces cada uno. Realiza primero la versión sin `Lock` (para evidenciar valores erróneos) y luego protégela con un `Lock`, mostrando el resultado correcto (`100 000`).

**Extracto clave con sincronización**:

```python
from multiprocessing import Process, Value, Lock

def inc(v, n, lock):
    for _ in range(n):
        with lock:
            v.value += 1

if __name__ == '__main__':
    N = 50_000
    contador = Value('i', 0)
    lock = Lock()
    p1 = Process(target=inc, args=(contador, N, lock))
    p2 = Process(target=inc, args=(contador, N, lock))
    p1.start(); p2.start(); p1.join(); p2.join()
    print('Resultado seguro:', contador.value)
```

*Comentario*: `Value` permite memoria compartida; el `Lock` garantiza atomicidad.

---

#### Ejercicio 4 · Nivel Avanzado

> **Objetivo**: medir el impacto del GIL versus `multiprocessing` en tareas CPU‑bound.
>
> **Enunciado**: implementa la función `fibonacci(n)` de forma recursiva e imprímela para `n = 35`. Mide primero el tiempo usando hilos (`threading.Thread`) con 4 hilos y luego con 4 procesos (`multiprocessing.Process`). Compara y explica la diferencia.

**Guía de solución**: se espera que la versión con hilos no supere la ejecución secuencial debido al GIL, mientras que la versión con procesos reduzca casi 4 × el tiempo. Se deben usar `time.perf_counter()` y presentar los números.

---

#### Ejercicio 5 · Nivel Experto

> **Objetivo**: diseñar un pipeline productor–consumidor usando `Pipe` doble.
>
> **Enunciado**: crea dos procesos hijos: `productor` genera 10 números pseudo‑aleatorios y los envía al padre; el padre los reenvía a un `consumidor`, que imprime el cuadrado de cada número. Implementa el pipeline con dos `Pipe()`, asegurando el cierre limpio de extremos y detectando fin de datos mediante envío del valor `None`.

**Esqueleto de solución** (fragmentos):

```python
from multiprocessing import Process, Pipe
import random, time

def productor(conn):
    for _ in range(10):
        conn.send(random.randint(1, 100))
        time.sleep(0.1)
    conn.send(None)  # señal de fin
    conn.close()

def consumidor(conn):
    while True:
        dato = conn.recv()
        if dato is None:
            break
        print('Cuadrado:', dato**2)
    conn.close()

if __name__ == '__main__':
    p_in, c_in = Pipe()   # productor → padre
    p_out, c_out = Pipe() # padre → consumidor

    prod = Process(target=productor, args=(p_in,))
    cons = Process(target=consumidor, args=(c_out,))
    prod.start(); cons.start()

    while True:
        val = c_in.recv()
        if val is None:
            p_out.send(None)
            break
        p_out.send(val)

    prod.join(); cons.join()
```

*Comentario*: se manejan dos pipes independientes y señal de terminación.

---

### Parte II · Ejercicios Propuestos (sin resolver)

#### Ejercicio 6 · Nivel Intermedio

Implementa un cronómetro compartido: tres procesos actualizan cada segundo un valor `Value('d')` con el instante actual. Un cuarto proceso lee el valor cada 0,5 s y registra si hay incoherencias temporales (> 1 s de salto), demostrando la necesidad de sincronización.

---

#### Ejercicio 7 · Nivel Intermedio +

Desarrolla un *load balancer* simple: un proceso maestro reparte una lista de URLs a descargar entre `k` procesos *worker* mediante una `Queue`. Cada *worker* registra su PID y el tiempo de descarga. Al finalizar, el maestro debe generar un reporte ordenado por duración.

---

#### Ejercicio 8 · Nivel Avanzado

Crea un programa que lance `N = 8` procesos calculando números primos en rangos disjuntos. Sincroniza el acceso a un archivo común `primos.txt` usando `Lock` para añadir los resultados sin colisiones. Mide el speed‑up frente a la versión secuencial.

---

#### Ejercicio 9 · Nivel Avanzado +

Construye una simulación de banco: múltiples cajeros (procesos) atienden clientes retirando y depositando sobre un mismo balance compartido (`Value`). Implementa una política de back‑off exponencial para reintentos cuando el `Lock` esté ocupado y registra métricas de contención.

---

#### Ejercicio 10 · Nivel Experto

Diseña un *benchmark* que compare tres métodos de IPC (`Pipe`, `Queue`, `multiprocessing.Manager().list`) transfiriendo un millón de enteros entre dos procesos. Grafica los tiempos medios y discute las causas de las diferencias.

---

¡Éxitos programando! Cada ejercicio te acercará a dominar la concurrencia en Python de forma sólida y eficiente.
