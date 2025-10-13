# concurrent.futures: Paralelismo sin dolor de cabeza

## Introducción: El problema del paralelismo real

Hasta ahora hemos hablado de `asyncio`, que nos da **concurrencia**: muchas tareas progresando al mismo tiempo en un solo hilo, aprovechando tiempos de espera. Pero hay un límite fundamental: si tu tarea es puro cómputo (calcular números primos, procesar imágenes, comprimir datos), `asyncio` no te ayuda. ¿Por qué? Porque solo tienes un núcleo de CPU trabajando.

Para obtener **paralelismo real**—múltiples CPUs calculando simultáneamente—necesitas otra herramienta. Entra `concurrent.futures`.

### La diferencia fundamental

Imagina una cocina:

**Concurrencia (asyncio):**
- Un chef muy hábil
- Pone una olla al fuego, mientras hierve pica cebollas
- Mientras las cebollas se doran, prepara una salsa
- **Un trabajador, muchas tareas entrelazadas**
- Perfecto cuando las tareas esperan (I/O)

**Paralelismo (concurrent.futures):**
- Varios chefs trabajando simultáneamente
- Cada uno con su propia estación
- Todos cocinando platos diferentes **al mismo tiempo**
- **Múltiples trabajadores, trabajando en paralelo**
- Necesario cuando las tareas son puro cómputo

### El GIL: El elefante en la habitación

Python tiene un problema único: el **Global Interpreter Lock (GIL)**. Es un mutex (candado) que permite que solo un hilo ejecute bytecode de Python a la vez, incluso en CPUs multi-core.

Esto significa que los threads tradicionales de Python no dan paralelismo real para código CPU-bound:

```python
import threading
import time

def calcular():
    """Tarea CPU-bound"""
    total = 0
    for i in range(10_000_000):
        total += i
    return total

inicio = time.time()

# Dos threads
t1 = threading.Thread(target=calcular)
t2 = threading.Thread(target=calcular)

t1.start()
t2.start()
t1.join()
t2.join()

print(f"Tiempo con threads: {time.time() - inicio:.2f}s")
# En una máquina dual-core: ~1.5s (casi lo mismo que secuencial)
```

Los threads se turnan el GIL, por eso no hay speedup. Pero `concurrent.futures` tiene la solución: **procesos**.

---

## Arquitectura de concurrent.futures

El módulo `concurrent.futures` proporciona dos executors (ejecutores) que abstraen la complejidad de threads y procesos:

### 1. ThreadPoolExecutor

**Usa threads del sistema operativo:**
- Comparten la misma memoria
- Limitados por el GIL para código Python
- **Buenos para I/O-bound:** leer archivos, peticiones HTTP, consultas a DB
- Bajo overhead de creación

**Cuándo usarlo:**
```python
# ✓ Bueno: I/O-bound
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(requests.get, url) for url in urls]

# ✗ Malo: CPU-bound
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(calcular_primos, n) for n in numeros]
    # No hay speedup por el GIL
```

### 2. ProcessPoolExecutor

**Usa procesos separados:**
- Cada proceso tiene su propia memoria y su propio GIL
- **Buenos para CPU-bound:** cálculos matemáticos, procesamiento de imágenes
- Overhead mayor (crear proceso ~100ms, thread ~1ms)
- Los datos se pasan mediante serialización (pickle)

**Cuándo usarlo:**
```python
# ✓ Excelente: CPU-bound
with ProcessPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(calcular_primos, n) for n in numeros]
    # Speedup real en multi-core

# ✗ Ineficiente: objetos no serializables
with ProcessPoolExecutor() as executor:
    # Esto falla si 'datos' no es pickleable
    futures = [executor.submit(procesar, datos) for datos in lista]
```

### La API unificada

Lo hermoso de `concurrent.futures` es que ambos executors tienen la **misma interfaz**:

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def tarea(x):
    return x * 2

# Puedes intercambiarlos fácilmente
for ExecutorClass in [ThreadPoolExecutor, ProcessPoolExecutor]:
    with ExecutorClass(max_workers=4) as executor:
        resultados = executor.map(tarea, range(10))
        print(list(resultados))
```

---

## Conceptos clave

### Futures: Promesas de resultados

Un `Future` es un objeto que representa un cálculo que puede o no haber terminado:

```python
from concurrent.futures import ThreadPoolExecutor
import time

def tarea_lenta(n):
    time.sleep(2)
    return n * 2

executor = ThreadPoolExecutor(max_workers=2)

# submit() retorna un Future inmediatamente
future = executor.submit(tarea_lenta, 10)

print(f"Future creado: {future}")
print(f"¿Está corriendo? {future.running()}")
print(f"¿Terminó? {future.done()}")

# result() bloquea hasta que termine
resultado = future.result()  # Espera ~2s aquí
print(f"Resultado: {resultado}")

executor.shutdown()
```

**Métodos importantes de Future:**
- `done()` - ¿Ya terminó?
- `running()` - ¿Está ejecutándose ahora?
- `result(timeout=None)` - Obtener resultado (bloquea si no está listo)
- `exception()` - Obtener excepción si falló
- `cancel()` - Intentar cancelar (solo si no empezó)

### as_completed: Procesar según terminen

A menudo quieres procesar resultados apenas estén listos, sin esperar a que todos terminen:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

def tarea(id):
    duracion = random.uniform(1, 3)
    time.sleep(duracion)
    return f"Tarea {id} tardó {duracion:.2f}s"

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(tarea, i) for i in range(5)]
    
    # Procesar según terminan (no en orden)
    for future in as_completed(futures):
        print(future.result())
```

Output (orden variable):
```
Tarea 2 tardó 1.23s
Tarea 0 tardó 1.45s
Tarea 4 tardó 1.89s
Tarea 1 tardó 2.34s
Tarea 3 tardó 2.67s
```

### map vs submit

Hay dos formas de enviar trabajo a un executor:

**executor.map()** - Simple, para casos básicos:
```python
with ProcessPoolExecutor() as executor:
    # Aplica función a cada elemento
    resultados = executor.map(funcion, lista)
    # Retorna iterador en el MISMO ORDEN que la entrada
```

**executor.submit()** - Más control:
```python
with ProcessPoolExecutor() as executor:
    # Más flexibilidad: diferentes funciones, argumentos, etc.
    futures = [
        executor.submit(funcion1, x),
        executor.submit(funcion2, y, z),
    ]
    # Puedes usar as_completed() para procesar según terminen
```

---

## Ejemplos prácticos resueltos

### Ejemplo 1: Procesamiento de imágenes en paralelo

**Escenario:** Tienes 100 imágenes y necesitas aplicar un filtro a cada una. Esto es CPU-bound puro.

```python
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageFilter
import time
from pathlib import Path

def procesar_imagen(ruta_entrada):
    """Aplica blur a una imagen"""
    try:
        # Abrir imagen
        img = Image.open(ruta_entrada)
        
        # Aplicar filtro (operación CPU-bound)
        img_procesada = img.filter(ImageFilter.GaussianBlur(radius=5))
        
        # Guardar resultado
        ruta_salida = Path("procesadas") / ruta_entrada.name
        img_procesada.save(ruta_salida)
        
        return f"✓ {ruta_entrada.name}"
    
    except Exception as e:
        return f"✗ {ruta_entrada.name}: {e}"

def procesar_secuencial(imagenes):
    """Versión secuencial para comparación"""
    inicio = time.time()
    
    for imagen in imagenes:
        procesar_imagen(imagen)
    
    return time.time() - inicio

def procesar_paralelo(imagenes, num_workers=None):
    """Versión paralela con ProcessPoolExecutor"""
    inicio = time.time()
    
    # None usa cpu_count()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # map() mantiene el orden
        resultados = executor.map(procesar_imagen, imagenes)
        
        # Consumir el iterador
        for resultado in resultados:
            print(resultado)
    
    return time.time() - inicio

# Uso
if __name__ == "__main__":
    Path("procesadas").mkdir(exist_ok=True)
    imagenes = list(Path("imagenes").glob("*.jpg"))
    
    print(f"Procesando {len(imagenes)} imágenes...\n")
    
    # Comparación
    tiempo_seq = procesar_secuencial(imagenes[:10])  # Solo 10 para test
    print(f"\nSecuencial: {tiempo_seq:.2f}s")
    
    tiempo_par = procesar_paralelo(imagenes[:10], num_workers=4)
    print(f"Paralelo (4 cores): {tiempo_par:.2f}s")
    print(f"Speedup: {tiempo_seq/tiempo_par:.2f}x")
```

**Resultados típicos en quad-core:**
```
Secuencial: 12.3s
Paralelo (4 cores): 3.4s
Speedup: 3.6x
```

**Puntos clave:**
- `if __name__ == "__main__":` es **obligatorio** con ProcessPoolExecutor en Windows
- El speedup nunca es perfecto (overhead de comunicación entre procesos)
- PIL/Pillow libera el GIL durante operaciones pesadas, pero aún así los procesos son mejores

---

### Ejemplo 2: Web scraper con ThreadPoolExecutor

**Escenario:** Descargar datos de 50 URLs. Esto es I/O-bound, perfecto para threads.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time

def descargar_url(url):
    """Descarga una URL y retorna estadísticas"""
    try:
        inicio = time.time()
        response = requests.get(url, timeout=10)
        duracion = time.time() - inicio
        
        return {
            "url": url,
            "status": response.status_code,
            "tamaño": len(response.content),
            "duracion": duracion,
            "exito": response.status_code == 200
        }
    
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "exito": False
        }

def scraper_secuencial(urls):
    """Versión secuencial"""
    inicio = time.time()
    resultados = [descargar_url(url) for url in urls]
    return resultados, time.time() - inicio

def scraper_concurrente(urls, max_workers=10):
    """Versión con threads"""
    inicio = time.time()
    resultados = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Crear futures
        future_to_url = {
            executor.submit(descargar_url, url): url 
            for url in urls
        }
        
        # Procesar según terminan
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                resultado = future.result()
                resultados.append(resultado)
                
                status = "✓" if resultado.get("exito") else "✗"
                print(f"{status} {url[:50]}")
                
            except Exception as e:
                print(f"✗ {url}: {e}")
    
    return resultados, time.time() - inicio

# Uso
if __name__ == "__main__":
    urls = [
        "https://www.python.org",
        "https://docs.python.org",
        "https://pypi.org",
        # ... más URLs
    ] * 10  # 30 URLs total
    
    print("=== SECUENCIAL ===")
    resultados_seq, tiempo_seq = scraper_secuencial(urls[:5])
    print(f"Tiempo: {tiempo_seq:.2f}s\n")
    
    print("=== CONCURRENTE (10 threads) ===")
    resultados_con, tiempo_con = scraper_concurrente(urls[:5], max_workers=10)
    print(f"Tiempo: {tiempo_con:.2f}s")
    print(f"Speedup: {tiempo_seq/tiempo_con:.2f}x")
    
    # Estadísticas
    exitosos = sum(1 for r in resultados_con if r.get("exito"))
    print(f"\n📊 Éxito: {exitosos}/{len(resultados_con)}")
```

**Puntos clave:**
- ThreadPoolExecutor es perfecto para I/O (el GIL no importa porque esperamos red)
- `as_completed()` procesa resultados apenas llegan (mejor UX)
- `future_to_url` mapea futures a contexto adicional (patrón común)

---

### Ejemplo 3: Procesamiento de CSV grandes con chunks

**Escenario:** Procesar un CSV de 10M de filas, haciendo cálculos en cada chunk.

```python
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import numpy as np
import time

def procesar_chunk(chunk_data):
    """Procesa un chunk de datos (CPU-bound)"""
    chunk_id, df_chunk = chunk_data
    
    # Operaciones pesadas
    df_chunk['cuadrado'] = df_chunk['valor'] ** 2
    df_chunk['raiz'] = np.sqrt(df_chunk['valor'])
    df_chunk['log'] = np.log(df_chunk['valor'] + 1)
    
    # Agregaciones
    estadisticas = {
        'chunk_id': chunk_id,
        'filas': len(df_chunk),
        'suma': df_chunk['valor'].sum(),
        'promedio': df_chunk['valor'].mean(),
        'std': df_chunk['valor'].std(),
    }
    
    return estadisticas

def crear_csv_prueba(nombre, num_filas=1_000_000):
    """Crea un CSV de prueba"""
    df = pd.DataFrame({
        'id': range(num_filas),
        'valor': np.random.randint(1, 1000, num_filas),
        'categoria': np.random.choice(['A', 'B', 'C'], num_filas)
    })
    df.to_csv(nombre, index=False)
    print(f"Creado {nombre} con {num_filas:,} filas")

def procesar_csv_paralelo(archivo, chunk_size=100_000, max_workers=4):
    """Lee CSV en chunks y procesa en paralelo"""
    inicio = time.time()
    
    # Leer chunks
    chunks = []
    for i, chunk in enumerate(pd.read_csv(archivo, chunksize=chunk_size)):
        chunks.append((i, chunk))
    
    print(f"CSV dividido en {len(chunks)} chunks")
    
    # Procesar en paralelo
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        resultados = list(executor.map(procesar_chunk, chunks))
    
    # Consolidar resultados
    total_filas = sum(r['filas'] for r in resultados)
    suma_total = sum(r['suma'] for r in resultados)
    promedio_global = suma_total / total_filas
    
    duracion = time.time() - inicio
    
    print(f"\n✓ Procesadas {total_filas:,} filas en {duracion:.2f}s")
    print(f"  Suma total: {suma_total:,.0f}")
    print(f"  Promedio: {promedio_global:.2f}")
    
    return resultados

# Uso
if __name__ == "__main__":
    archivo = "datos_grandes.csv"
    
    # Crear archivo de prueba si no existe
    from pathlib import Path
    if not Path(archivo).exists():
        crear_csv_prueba(archivo, num_filas=1_000_000)
    
    # Procesar
    resultados = procesar_csv_paralelo(
        archivo, 
        chunk_size=100_000,
        max_workers=4
    )
```

**Puntos clave:**
- Dividir trabajo en chunks balanceados es clave
- Pandas puede ser CPU-bound en operaciones complejas
- Los procesos no comparten memoria, hay que consolidar resultados

---

### Ejemplo 4: Control de errores y timeouts

**Escenario:** Ejecutar tareas que pueden fallar o tardar mucho.

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
import time
import random

def tarea_impredecible(id):
    """Tarea que puede fallar o tardar mucho"""
    tipo = random.choice(['rapida', 'lenta', 'error'])
    
    if tipo == 'rapida':
        time.sleep(1)
        return f"Tarea {id}: OK (rápida)"
    
    elif tipo == 'lenta':
        time.sleep(10)
        return f"Tarea {id}: OK (lenta)"
    
    else:  # error
        time.sleep(0.5)
        raise ValueError(f"Tarea {id} falló intencionalmente")

def ejecutar_con_manejo_errores(num_tareas, timeout_por_tarea=3):
    """Ejecuta tareas con manejo robusto de errores y timeouts"""
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Enviar todas las tareas
        futures = {
            executor.submit(tarea_impredecible, i): i 
            for i in range(num_tareas)
        }
        
        resultados_exitosos = []
        errores = []
        timeouts = []
        
        # Procesar según terminan
        for future in as_completed(futures, timeout=15):  # Timeout global
            task_id = futures[future]
            
            try:
                # Timeout individual por tarea
                resultado = future.result(timeout=timeout_por_tarea)
                resultados_exitosos.append(resultado)
                print(f"✓ {resultado}")
                
            except TimeoutError:
                timeouts.append(task_id)
                print(f"⏱️  Tarea {task_id}: Timeout (>{timeout_por_tarea}s)")
                future.cancel()  # Intentar cancelar
                
            except Exception as e:
                errores.append((task_id, str(e)))
                print(f"✗ Tarea {task_id}: {e}")
    
    # Reporte final
    print(f"\n📊 Resumen:")
    print(f"  Exitosas: {len(resultados_exitosos)}")
    print(f"  Timeouts: {len(timeouts)}")
    print(f"  Errores: {len(errores)}")
    
    return resultados_exitosos, errores, timeouts

# Uso
if __name__ == "__main__":
    ejecutar_con_manejo_errores(num_tareas=10, timeout_por_tarea=3)
```

**Puntos clave:**
- `future.result(timeout=N)` - timeout individual por tarea
- `as_completed(futures, timeout=N)` - timeout global para todas
- `future.cancel()` intenta cancelar, pero solo funciona si no empezó
- Siempre manejar excepciones, las tareas pueden fallar

---

### Ejemplo 5: Pool dinámico con callback

**Escenario:** Procesar tareas y ejecutar acciones según terminen, sin bloquear.

```python
from concurrent.futures import ThreadPoolExecutor
import time
import random

def tarea(id):
    """Tarea que tarda tiempo variable"""
    duracion = random.uniform(1, 3)
    time.sleep(duracion)
    
    # Simular fallo ocasional
    if random.random() < 0.2:
        raise Exception(f"Tarea {id} falló")
    
    return {"id": id, "duracion": duracion}

def on_tarea_completa(future):
    """Callback ejecutado cuando una tarea termina"""
    try:
        resultado = future.result()
        print(f"✓ Tarea {resultado['id']} completada en {resultado['duracion']:.2f}s")
        
        # Aquí podrías hacer algo útil: guardar en DB, notificar, etc.
        
    except Exception as e:
        print(f"✗ Tarea falló: {e}")

def pool_con_callbacks(num_tareas):
    """Executor con callbacks para no bloquear"""
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Enviar tareas con callback
        for i in range(num_tareas):
            future = executor.submit(tarea, i)
            # add_done_callback() se ejecuta cuando termina
            future.add_done_callback(on_tarea_completa)
        
        # El executor espera a todas en el __exit__
        print("Tareas enviadas, esperando...")
    
    print("\n✓ Todas las tareas procesadas")

# Uso
if __name__ == "__main__":
    pool_con_callbacks(num_tareas=10)
```

**Puntos clave:**
- `add_done_callback()` ejecuta función cuando el future termina
- El callback recibe el future como argumento
- Útil para arquitecturas event-driven

---

## Ejercicios para resolver

### Ejercicio 1: Compresor de archivos paralelo

**Objetivo:** Comprimir múltiples archivos en paralelo usando diferentes algoritmos.

**Requisitos:**
1. Crear 10 archivos de texto con contenido aleatorio
2. Comprimir cada uno con gzip usando ProcessPoolExecutor
3. Comparar tiempo secuencial vs paralelo
4. Calcular ratio de compresión promedio
5. Mostrar progreso: "Comprimido 3/10 archivos..."

**Pistas:**
```python
import gzip
import shutil
from pathlib import Path

def comprimir_archivo(ruta_entrada):
    ruta_salida = ruta_entrada.with_suffix('.gz')
    with open(ruta_entrada, 'rb') as f_in:
        with gzip.open(ruta_salida, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # Retornar estadísticas
    return {
        'archivo': ruta_entrada.name,
        'tamaño_original': ruta_entrada.stat().st_size,
        'tamaño_comprimido': ruta_salida.stat().st_size
    }
```

---

### Ejercicio 2: Validador de emails concurrente

**Objetivo:** Validar emails verificando si el dominio existe (DNS lookup).

**Requisitos:**
1. Tener una lista de 100 emails
2. Para cada email, hacer DNS lookup del dominio (I/O-bound)
3. Usar ThreadPoolExecutor con 20 workers
4. Clasificar: válidos, inválidos, no verificables
5. Implementar timeout de 5s por verificación

**Pistas:**
```python
import dns.resolver
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def verificar_email(email):
    try:
        dominio = email.split('@')[1]
        # DNS lookup (I/O-bound)
        dns.resolver.resolve(dominio, 'MX')
        return (email, 'valido')
    except:
        return (email, 'invalido')
```

---

### Ejercicio 3: Calculadora de números primos distribuida

**Objetivo:** Encontrar todos los números primos en un rango grande.

**Requisitos:**
1. Rango: 1 a 1,000,000
2. Dividir en chunks (ej: 100 chunks de 10,000 números)
3. Usar ProcessPoolExecutor para procesar chunks en paralelo
4. Implementar algoritmo eficiente (criba de Eratóstenes por chunk)
5. Comparar con versión secuencial

**Pistas:**
```python
def es_primo(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def encontrar_primos_en_rango(inicio, fin):
    return [n for n in range(inicio, fin) if es_primo(n)]
```

---

### Ejercicio 4: Monitor de recursos del sistema

**Objetivo:** Monitorear CPU, memoria y disco cada 5 segundos usando threads.

**Requisitos:**
1. Crear 3 funciones: `monitorear_cpu()`, `monitorear_memoria()`, `monitorear_disco()`
2. Cada función lee métricas cada 5s y las guarda en una lista compartida
3. Usar ThreadPoolExecutor con 3 workers permanentes
4. Función principal que cada 30s calcula promedios y muestra reporte
5. Graceful shutdown con Ctrl+C

**Pistas:**
```python
import psutil
import time
from concurrent.futures import ThreadPoolExecutor

def monitorear_cpu(resultados, intervalo=5):
    while not detenerse.is_set():
        cpu = psutil.cpu_percent(interval=1)
        resultados['cpu'].append(cpu)
        time.sleep(intervalo)
```

---

### Ejercicio 5: Downloader con sistema de colas

**Objetivo:** Sistema de descarga con cola de prioridad y reintentos.

**Requisitos:**
1. Cola con 3 niveles de prioridad: alta, media, baja
2. ThreadPoolExecutor que procesa URLs según prioridad
3. Si una descarga falla, reintentar hasta 3 veces con backoff
4. Guardar archivos descargados con hash MD5 en el nombre
5. Log de todas las operaciones

**Estructura:**
```python
import queue
import hashlib
from concurrent.futures import ThreadPoolExecutor

class DownloadQueue:
    def __init__(self, max_workers=5):
        self.queue = queue.PriorityQueue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def add_download(self, url, prioridad=2):
        # prioridad: 0=alta, 1=media, 2=baja
        self.queue.put((prioridad, url))
    
    def procesar(self):
        # Tu código aquí
        pass
```

---

### Ejercicio 6: MapReduce simple

**Objetivo:** Implementar un sistema MapReduce básico para contar palabras en múltiples archivos.

**Requisitos:**
1. **Map phase:** Cada proceso cuenta palabras en un archivo
2. **Shuffle phase:** Agrupa conteos por palabra
3. **Reduce phase:** Suma conteos totales por palabra
4. Usar ProcessPoolExecutor para ambas fases
5. Procesar al menos 10 archivos de texto grandes

**Estructura:**
```python
from concurrent.futures import ProcessPoolExecutor
from collections import defaultdict

def map_phase(archivo):
    """Retorna dict {palabra: cuenta} para un archivo"""
    conteo = defaultdict(int)
    # Tu código aquí
    return conteo

def reduce_phase(conteos_parciales):
    """Combina múltiples dicts en uno"""
    conteo_final = defaultdict(int)
    # Tu código aquí
    return conteo_final

def mapreduce_paralelo(archivos):
    with ProcessPoolExecutor() as executor:
        # Map
        conteos_parciales = executor.map(map_phase, archivos)
        
        # Reduce (puede ser paralelo también)
        # Tu código aquí
        pass
```

---

## Patrones avanzados y mejores prácticas

### 1. Context manager personalizado

```python
from concurrent.futures import ThreadPoolExecutor

class MiExecutor:
    def __init__(self, max_workers):
        self.max_workers = max_workers
        self.executor = None
    
    def __enter__(self):
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)
    
    def submit(self, fn, *args, **kwargs):
        return self.executor.submit(fn, *args, **kwargs)

# Uso
with MiExecutor(max_workers=4) as executor:
    futures = [executor.submit(tarea, i) for i in range(10)]
```

### 2. Limitar uso de memoria con Semaphore

```python
from concurrent.futures import ThreadPoolExecutor
import threading

MAX_EN_MEMORIA = 5
semaforo = threading.Semaphore(MAX_EN_MEMORIA)

def tarea_con_alto_uso_memoria(datos):
    with semaforo:  # Solo 5 tareas simultáneas
        # Procesar datos grandes
        resultado = procesar(datos)
        return resultado

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(tarea_con_alto_uso_memoria, d) for d in datos]
```

### 3. Progreso con tqdm

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def procesar(item):
    # Procesar
    return resultado

items = range(100)

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(procesar, item) for item in items]
    
    # Barra de progreso
    for future in tqdm(as_completed(futures), total=len(futures)):
        resultado = future.result()
```

---

## Debugging y troubleshooting

### Problema 1: "BrokenProcessPool"

```python
# ✗ Malo: función no es pickleable
class Procesador:
    def __init__(self, config):
        self.config = config
    
    def procesar(self, datos):
        return datos * self.config

# En ProcessPoolExecutor esto falla
```

**Solución:** Usa funciones top-level o módulos externos

```python
# ✓ Bueno
def procesar(datos, config):
    return datos * config

# O define la clase en un módulo separado
```

### Problema 2: Deadlock con locks

```python
# ✗ Malo: puede hacer deadlock
lock = threading.Lock()

def tarea1():
    with lock:
        time.sleep(1)
        # Llamar otra función que necesita el lock
        tarea2()

def tarea2():
    with lock:  # Deadlock!
        pass
```

**Solución:** Usa RLock (reentrant lock) o evita locks anidados

### Problema 3: Demasiados workers

```python
# ✗ Malo: crear 1000 threads
with ThreadPoolExecutor(max_workers=1000) as executor:
    pass
```

**Regla general:**
- **I/O-bound:** `max_workers = 10-100` (depende de latencia)
- **CPU-bound:** `max_workers = cpu_count()` (o `cpu_count() - 1`)

---

## Conclusión: Cuándo usar qué

| Escenario | Herramienta | Razón |
|-----------|-------------|-------|
| Cálculos matemáticos intensivos | ProcessPoolExecutor | Paralelismo real, evita GIL |
| 100 peticiones HTTP | ThreadPoolExecutor | I/O-bound, threads eficientes |
| Procesamiento de 1000 imágenes | ProcessPoolExecutor | CPU-bound, necesita multi-core |
| Chat server con muchos clientes | asyncio | Concurrencia masiva, bajo overhead |
| Leer 50 archivos del disco | ThreadPoolExecutor | I/O-bound, threads suficientes |
| Pipeline ETL con transformaciones | ProcessPoolExecutor | CPU-bound en transformaciones |

**Regla de oro:**
- **I/O-bound + pocas tareas (< 1000):** ThreadPoolExecutor
- **I/O-bound + muchas tareas (> 1000):** asyncio
- **CPU-bound:** ProcessPoolExecutor

¡Ahora tienes el poder del paralelismo real en tus manos!