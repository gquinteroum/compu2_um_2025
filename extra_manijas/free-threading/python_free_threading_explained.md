# Python Free-Threading: el fin del GIL (Global Interpreter Lock)

## Qué es el GIL
El **Global Interpreter Lock (GIL)** es un mecanismo introducido en las primeras versiones de **CPython** (la implementación principal de Python) para simplificar la gestión de memoria. Su función es garantizar que **solo un hilo de Python ejecute bytecode a la vez**, incluso en sistemas con múltiples núcleos.

Esto significa que, aunque Python permite crear múltiples hilos (`threading.Thread`), en realidad **solo uno puede ejecutar código de Python puro al mismo tiempo**. Por eso, las aplicaciones CPU-bound (que realizan mucho cálculo) no se benefician de varios núcleos usando hilos: el GIL se convierte en un cuello de botella.

---

## Historia
- **Década de 1990:** El GIL se introduce en CPython como una forma sencilla de evitar condiciones de carrera en la gestión del recolector de basura y objetos compartidos.
- **Durante años:** Aunque criticado, se mantuvo porque simplificaba el desarrollo de extensiones C y mejoraba el rendimiento en programas de un solo hilo.
- **Intentos previos:** Se hicieron varios intentos de eliminarlo (notablemente el de Greg Stein en 2000), pero todos introducían pérdidas significativas de rendimiento o complejidad.
- **Python 3.13:** Se lanza una build experimental con la opción `--disable-gil`.
- **Python 3.14:** Esta versión oficializa el soporte de **free-threading** (sin GIL), permitiendo compilaciones donde múltiples hilos pueden ejecutar código Python en paralelo.

---

## Qué cambia con el Free-Threading
El nuevo modelo elimina el bloqueo global del intérprete. En su lugar, se utilizan mecanismos de sincronización más finos (por objeto o por estructura) y cambios internos en el recolector de basura para permitir **paralelismo real entre hilos**.

Esto significa que, en un build sin GIL, si se lanzan cuatro hilos en una CPU de cuatro núcleos, **los cuatro pueden ejecutar código Python simultáneamente**.

Sin embargo:
- El rendimiento en programas de un solo hilo puede bajar entre un 5 y un 15 %.
- Muchas librerías en C deben adaptarse para ser seguras en entornos sin GIL.

---

## Cómo compilar Python 3.14 sin GIL (modo free-threaded)

### 1. Crear un Dockerfile basado en Debian Trixie

```dockerfile
FROM debian:trixie-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential wget zlib1g-dev libncurses5-dev libssl-dev \
    libreadline-dev libffi-dev libsqlite3-dev tk-dev uuid-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src

RUN wget https://www.python.org/ftp/python/3.14.0/Python-3.14.0.tgz && \
    tar -xf Python-3.14.0.tgz && \
    cd Python-3.14.0 && \
    ./configure --disable-gil --enable-optimizations --prefix=/usr/local && \
    make -j"$(nproc)" && make install && \
    cd .. && rm -rf Python-3.14.0*

WORKDIR /app
CMD ["python3"]
```

### 2. Construir la imagen
```bash
docker build -t python:3.14-nogil .
```

### 3. Verificar
```bash
docker run -it --rm python:3.14-nogil python3 -c "import sys; print(sys._is_gil_enabled())"
```
Debería imprimir `False`.

---

## Cómo usar la versión con GIL

```bash
docker run -it --rm python:3.14-slim python3 -c "import sys; print(sys.version)"
```
Esta versión usa el build clásico con GIL.

---

## Benchmark de rendimiento
Crea un archivo `benchmark_threads.py` con este contenido:

```python
import threading, time, math, sys

def heavy_computation(n):
    total = 0.0
    for i in range(1, n):
        total += math.sqrt(i) * math.sin(i) * math.cos(i/2)
    return total

def run_test(num_threads, n):
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

if __name__ == "__main__":
    print(f"Python version: {sys.version.split()[0]}")
    try:
        print(f"GIL enabled: {sys._is_gil_enabled()}")
    except AttributeError:
        pass
    print("\nRunning benchmark...\n")
    for threads in [1, 2, 4, 8]:
        run_test(threads, 10_000_000)
```

### Ejecutar con GIL
```bash
docker run -v $(pwd):/app -w /app python:3.14-slim python3 benchmark_threads.py
```

### Ejecutar sin GIL
```bash
docker run -v $(pwd):/app -w /app python:3.14-nogil python3 benchmark_threads.py
```

---

## Resultados esperados

**Con GIL:**
```
 1 threads -> 3.5 s
 2 threads -> 3.6 s
 4 threads -> 3.7 s
```

**Sin GIL:**
```
 1 threads -> 3.5 s
 2 threads -> 1.8 s
 4 threads -> 0.9 s
```

La diferencia muestra el impacto directo del GIL en tareas CPU-bound. En programas que dependen de I/O (entrada/salida), el cambio puede ser menos evidente, pero el free-threading representa el paso más grande en la historia reciente de Python hacia el paralelismo real.

