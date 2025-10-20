# Ejercicios prácticos de asyncio

## Instrucciones generales

Cada ejercicio está diseñado para que explores una parte específica del ecosistema asíncrono de Python. Los primeros 6 incluyen soluciones completas para que veas patrones comunes. Los últimos 6 son para que los resuelvas tú mismo.

**Instalación de dependencias necesarias:**
```bash
pip install aiohttp aiofiles motor asyncpg
```

---

## Ejercicios Resueltos

### Ejercicio 1: Descargador concurrente de imágenes

**Objetivo:** Descargar múltiples imágenes simultáneamente y guardarlas en disco usando `aiohttp` y `aiofiles`.

**Contexto:** `aiofiles` permite leer/escribir archivos de forma asíncrona sin bloquear el event loop.

```python
import asyncio
import aiohttp
import aiofiles
from pathlib import Path

async def descargar_imagen(session, url, nombre_archivo):
    """Descarga una imagen y la guarda en disco"""
    print(f"📥 Descargando {nombre_archivo}...")
    
    async with session.get(url) as response:
        if response.status == 200:
            # Leer el contenido como bytes
            contenido = await response.read()
            
            # Escribir el archivo de forma asíncrona
            async with aiofiles.open(f"descargas/{nombre_archivo}", "wb") as f:
                await f.write(contenido)
            
            print(f"✅ {nombre_archivo} descargado ({len(contenido)} bytes)")
        else:
            print(f"❌ Error descargando {nombre_archivo}: {response.status}")

async def main():
    # Crear directorio si no existe
    Path("descargas").mkdir(exist_ok=True)
    
    # Lista de imágenes a descargar
    imagenes = [
        ("https://picsum.photos/400/300", "imagen1.jpg"),
        ("https://picsum.photos/500/400", "imagen2.jpg"),
        ("https://picsum.photos/600/400", "imagen3.jpg"),
        ("https://picsum.photos/300/500", "imagen4.jpg"),
    ]
    
    # Crear una sesión compartida (más eficiente)
    async with aiohttp.ClientSession() as session:
        # Crear todas las tareas
        tareas = [
            descargar_imagen(session, url, nombre)
            for url, nombre in imagenes
        ]
        
        # Ejecutar concurrentemente
        await asyncio.gather(*tareas)
    
    print("\n🎉 Todas las descargas completadas")

if __name__ == "__main__":
    asyncio.run(main())
```

**Puntos clave:**
- `aiohttp.ClientSession()` se reutiliza para múltiples peticiones (más eficiente)
- `aiofiles.open()` no bloquea el event loop al escribir
- Todas las descargas ocurren concurrentemente

---

### Ejercicio 2: API REST básica con timeout

**Objetivo:** Consultar varias APIs simultáneamente con un timeout máximo por petición.

**Contexto:** En producción, siempre debes poner timeouts para evitar que una petición lenta bloquee todo.

```python
import asyncio
import aiohttp
from datetime import datetime

async def consultar_api(session, nombre, url, timeout_segundos=5):
    """Consulta una API con timeout"""
    try:
        inicio = datetime.now()
        
        # timeout_segundos aplica a toda la operación
        timeout = aiohttp.ClientTimeout(total=timeout_segundos)
        
        async with session.get(url, timeout=timeout) as response:
            datos = await response.json()
            
            duracion = (datetime.now() - inicio).total_seconds()
            print(f"✅ {nombre}: {response.status} ({duracion:.2f}s)")
            return {"api": nombre, "datos": datos, "duracion": duracion}
            
    except asyncio.TimeoutError:
        print(f"⏱️  {nombre}: Timeout después de {timeout_segundos}s")
        return {"api": nombre, "error": "timeout"}
        
    except Exception as e:
        print(f"❌ {nombre}: Error - {e}")
        return {"api": nombre, "error": str(e)}

async def main():
    apis = [
        ("JSONPlaceholder", "https://jsonplaceholder.typicode.com/posts/1"),
        ("GitHub", "https://api.github.com/users/github"),
        ("CoinGecko", "https://api.coingecko.com/api/v3/ping"),
        # Esta es lenta a propósito
        ("HTTPBin Delay", "https://httpbin.org/delay/10"),
    ]
    
    async with aiohttp.ClientSession() as session:
        tareas = [
            consultar_api(session, nombre, url, timeout_segundos=3)
            for nombre, url in apis
        ]
        
        resultados = await asyncio.gather(*tareas)
    
    print("\n📊 Resumen:")
    for resultado in resultados:
        print(f"  {resultado['api']}: {resultado.get('error', 'OK')}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Puntos clave:**
- `aiohttp.ClientTimeout` controla cuánto esperar
- `asyncio.gather()` espera todas las tareas, incluso si algunas fallan
- Los timeouts se manejan con `asyncio.TimeoutError`

---

### Ejercicio 3: Productor-Consumidor con asyncio.Queue

**Objetivo:** Implementar el patrón productor-consumidor usando colas asíncronas.

**Contexto:** Las colas asíncronas permiten comunicación segura entre corrutinas sin race conditions.

```python
import asyncio
import random

async def productor(queue, id_productor, num_items):
    """Produce items y los pone en la cola"""
    for i in range(num_items):
        await asyncio.sleep(random.uniform(0.1, 0.5))
        item = f"Item-{id_productor}-{i}"
        await queue.put(item)
        print(f"🏭 Productor {id_productor} creó: {item}")
    print(f"✅ Productor {id_productor} terminó")

async def consumidor(queue, id_consumidor):
    """Consume items de la cola"""
    while True:
        item = await queue.get()
        
        if item is None:
            queue.task_done()
            break
        
        await asyncio.sleep(random.uniform(0.2, 0.8))
        print(f"🔧 Consumidor {id_consumidor} procesó: {item}")
        queue.task_done()
    
    print(f"✅ Consumidor {id_consumidor} terminó")

async def main():
    queue = asyncio.Queue(maxsize=5)

    num_productores = 3
    items_por_productor = 4
    productores = [
        productor(queue, i, items_por_productor)
        for i in range(num_productores)
    ]

    num_consumidores = 2
    consumidores = [
        consumidor(queue, i)
        for i in range(num_consumidores)
    ]

    # ✅ Iniciar todos como tareas
    tareas_productores = [asyncio.create_task(p) for p in productores]
    tareas_consumidores = [asyncio.create_task(c) for c in consumidores]

    # Esperar productores
    await asyncio.gather(*tareas_productores)

    # Esperar procesamiento
    await queue.join()

    # Señal de término
    for _ in range(num_consumidores):
        await queue.put(None)

    # Esperar consumidores
    await asyncio.gather(*tareas_consumidores)

    print("\n🎉 Pipeline completado")

if __name__ == "__main__":
    asyncio.run(main())
```

**Puntos clave:**
- `queue.put()` bloquea si la cola está llena (backpressure automático)
- `queue.get()` bloquea si la cola está vacía
- `queue.join()` espera hasta que todos los items sean procesados
- `None` se usa como señal de terminación (patrón común)

---

### Ejercicio 4: Servidor TCP Echo mejorado

**Objetivo:** Crear un servidor TCP que maneja múltiples clientes concurrentemente con comandos especiales.

**Contexto:** `asyncio.start_server()` es perfecto para protocolos personalizados.

```python
import asyncio

class EstadoServidor:
    """Estado compartido entre todos los clientes"""
    def __init__(self):
        self.clientes_activos = 0
        self.mensajes_totales = 0

estado = EstadoServidor()

async def manejar_cliente(reader, writer):
    """Maneja un cliente individual"""
    addr = writer.get_extra_info('peername')
    print(f"🔌 Cliente conectado desde {addr}")
    
    estado.clientes_activos += 1
    
    try:
        # Mensaje de bienvenida
        writer.write(b"Bienvenido al servidor Echo!\n")
        writer.write(b"Comandos: /stats, /quit\n")
        await writer.drain()
        
        while True:
            # Leer datos (hasta 1024 bytes)
            data = await reader.read(1024)
            
            if not data:
                break
            
            mensaje = data.decode().strip()
            estado.mensajes_totales += 1
            
            # Procesar comandos
            if mensaje == "/quit":
                writer.write(b"Adios!\n")
                await writer.drain()
                break
                
            elif mensaje == "/stats":
                stats = (
                    f"Clientes activos: {estado.clientes_activos}\n"
                    f"Mensajes totales: {estado.mensajes_totales}\n"
                ).encode()
                writer.write(stats)
                await writer.drain()
                
            else:
                # Echo normal
                respuesta = f"Echo: {mensaje}\n".encode()
                writer.write(respuesta)
                await writer.drain()
    
    except Exception as e:
        print(f"❌ Error con cliente {addr}: {e}")
    
    finally:
        estado.clientes_activos -= 1
        print(f"👋 Cliente {addr} desconectado")
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(
        manejar_cliente,
        '127.0.0.1',
        8888
    )
    
    addr = server.sockets[0].getsockname()
    print(f"🚀 Servidor escuchando en {addr}")
    print("   Conéctate con: telnet localhost 8888")
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
```

**Puntos clave:**
- Cada cliente se maneja en su propia corrutina
- `reader.read()` y `writer.drain()` son operaciones asíncronas
- Estado compartido requiere cuidado (en casos complejos usa locks)
- `writer.wait_closed()` asegura limpieza apropiada

**Pruébalo:**
```bash
# Terminal 1: ejecuta el servidor
python ejercicio4.py

# Terminal 2: conéctate como cliente
telnet localhost 8888
```

---

### Ejercicio 5: Rate limiter (limitador de velocidad)

**Objetivo:** Implementar un rate limiter para controlar cuántas peticiones hacer por segundo.

**Contexto:** Al scrapear o usar APIs, necesitas respetar límites de velocidad.

```python
import asyncio
import aiohttp
import time
from collections import deque

class RateLimiter:
    """Limita operaciones a N por segundo"""
    
    def __init__(self, max_por_segundo):
        self.max_por_segundo = max_por_segundo
        self.timestamps = deque()
    
    async def esperar(self):
        """Espera si es necesario para respetar el rate limit"""
        ahora = time.time()
        
        # Limpiar timestamps viejos (más de 1 segundo)
        while self.timestamps and self.timestamps[0] < ahora - 1:
            self.timestamps.popleft()
        
        # Si alcanzamos el límite, esperar
        if len(self.timestamps) >= self.max_por_segundo:
            tiempo_espera = 1 - (ahora - self.timestamps[0])
            if tiempo_espera > 0:
                print(f"  ⏳ Rate limit alcanzado, esperando {tiempo_espera:.2f}s")
                await asyncio.sleep(tiempo_espera)
                # Recursión para volver a chequear
                await self.esperar()
        
        # Registrar este timestamp
        self.timestamps.append(time.time())

async def fetch_con_rate_limit(session, url, rate_limiter):
    """Hace petición respetando rate limit"""
    await rate_limiter.esperar()
    
    async with session.get(url) as response:
        return await response.text()

async def main():
    # Permitir solo 3 peticiones por segundo
    rate_limiter = RateLimiter(max_por_segundo=3)
    
    # Simular 10 peticiones
    urls = [f"https://httpbin.org/delay/0" for _ in range(10)]
    
    inicio = time.time()
    
    async with aiohttp.ClientSession() as session:
        tareas = [
            fetch_con_rate_limit(session, url, rate_limiter)
            for url in urls
        ]
        
        resultados = await asyncio.gather(*tareas)
    
    duracion = time.time() - inicio
    
    print(f"\n✅ Completadas {len(resultados)} peticiones en {duracion:.2f}s")
    print(f"   Velocidad promedio: {len(resultados)/duracion:.2f} req/s")

if __name__ == "__main__":
    asyncio.run(main())
```

**Puntos clave:**
- El rate limiter es reutilizable entre corrutinas
- Usa `deque` para mantener ventana deslizante de timestamps
- `asyncio.sleep()` no bloquea otras corrutinas
- Útil para respetar límites de APIs (ej: Twitter, GitHub)

---

### Ejercicio 6: Scraper con retry y exponential backoff

**Objetivo:** Implementar lógica de reintentos con espera exponencial para manejar fallos temporales.

**Contexto:** En el mundo real, las peticiones fallan. Necesitas estrategias de recuperación.

```python
import asyncio
import aiohttp
import random

async def fetch_con_retry(session, url, max_intentos=3, backoff_base=1):
    """
    Intenta fetch con reintentos exponenciales
    
    Args:
        session: ClientSession de aiohttp
        url: URL a descargar
        max_intentos: Número máximo de intentos
        backoff_base: Segundos base para backoff (se duplica cada intento)
    """
    for intento in range(1, max_intentos + 1):
        try:
            print(f"  🔄 Intento {intento}/{max_intentos} para {url}")
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    contenido = await response.text()
                    print(f"  ✅ Éxito en intento {intento}")
                    return contenido
                
                elif response.status >= 500:
                    # Error del servidor, vale la pena reintentar
                    print(f"  ⚠️  Error {response.status}, reintentando...")
                    
                else:
                    # Error del cliente (4xx), no vale la pena reintentar
                    print(f"  ❌ Error {response.status}, no reintentable")
                    return None
        
        except asyncio.TimeoutError:
            print(f"  ⏱️  Timeout en intento {intento}")
        
        except aiohttp.ClientError as e:
            print(f"  ❌ Error de red: {e}")
        
        # Si no es el último intento, esperar con backoff exponencial
        if intento < max_intentos:
            # Backoff exponencial con jitter
            espera = backoff_base * (2 ** (intento - 1))
            jitter = random.uniform(0, espera * 0.1)  # ±10% de variación
            tiempo_total = espera + jitter
            
            print(f"  ⏳ Esperando {tiempo_total:.2f}s antes de reintentar...")
            await asyncio.sleep(tiempo_total)
    
    print(f"  💔 Fallaron todos los intentos para {url}")
    return None

async def main():
    urls = [
        "https://httpbin.org/status/200",  # Siempre exitoso
        "https://httpbin.org/status/500",  # Siempre falla (servidor)
        "https://httpbin.org/status/404",  # Error cliente (no reintentable)
        "https://httpbin.org/delay/10",    # Timeout
    ]
    
    async with aiohttp.ClientSession() as session:
        tareas = [
            fetch_con_retry(session, url, max_intentos=3, backoff_base=1)
            for url in urls
        ]
        
        resultados = await asyncio.gather(*tareas)
    
    exitosos = sum(1 for r in resultados if r is not None)
    print(f"\n📊 Resultados: {exitosos}/{len(urls)} exitosos")

if __name__ == "__main__":
    asyncio.run(main())
```

**Puntos clave:**
- **Exponential backoff**: cada reintento espera el doble que el anterior
- **Jitter**: variación aleatoria para evitar "thundering herd"
- **Diferencia errores**: 5xx (reintentar) vs 4xx (no reintentar)
- Patrón usado por AWS, Google Cloud, etc.

---

## Ejercicios Para Resolver

### Ejercicio 7: Monitor de sitios web

**Objetivo:** Crear un programa que monitoree el estado de múltiples sitios web cada 30 segundos.

**Requisitos:**
1. Mantener una lista de URLs a monitorear
2. Cada 30 segundos, verificar todas las URLs concurrentemente
3. Registrar el tiempo de respuesta y código de estado
4. Si un sitio falla 3 veces consecutivas, mostrar una alerta
5. El programa debe correr indefinidamente hasta Ctrl+C

**Pistas:**
- Usa `asyncio.sleep(30)` en un loop infinito
- Mantén un diccionario de contadores de fallos por URL
- `asyncio.create_task()` para no bloquear el monitoreo

**Estructura sugerida:**
```python
import asyncio
import aiohttp
from datetime import datetime

async def verificar_sitio(session, url):
    # Tu código aquí
    pass

async def monitorear_sitios(urls, intervalo=30):
    # Tu código aquí
    pass

async def main():
    sitios = [
        "https://www.google.com",
        "https://www.github.com",
        # Agrega más...
    ]
    await monitorear_sitios(sitios)

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Ejercicio 8: Procesador de archivos batch

**Objetivo:** Leer múltiples archivos de texto concurrentemente y contar palabras totales.

**Requisitos:**
1. Crear 5 archivos de texto con contenido dummy
2. Leer todos los archivos concurrentemente usando `aiofiles`
3. Contar palabras en cada archivo
4. Calcular estadísticas: total de palabras, promedio por archivo, archivo más largo
5. Simular procesamiento lento con `await asyncio.sleep(random.uniform(0.1, 0.5))`

**Pistas:**
- `aiofiles.open(archivo, 'r')` para lectura asíncrona
- `.split()` para contar palabras
- `asyncio.gather()` con `return_exceptions=True` para manejar errores

---

### Ejercicio 9: Chat room simple

**Objetivo:** Implementar un servidor de chat donde múltiples clientes pueden enviarse mensajes.

**Requisitos:**
1. Servidor TCP que acepta múltiples clientes
2. Cuando un cliente se conecta, pide su nombre
3. Los mensajes de un cliente se broadcast a todos los demás
4. Comandos: `/list` (mostrar usuarios), `/quit` (desconectar)
5. Notificar a todos cuando alguien entra o sale

**Pistas:**
- Mantén un diccionario de `{writer: nombre}` para clientes activos
- Necesitas una función para broadcast a todos los clientes
- Usa `try/except` para manejar desconexiones abruptas

**Estructura sugerida:**
```python
import asyncio

clientes = {}  # {writer: nombre}

async def broadcast(mensaje, remitente=None):
    # Enviar mensaje a todos excepto remitente
    pass

async def manejar_cliente(reader, writer):
    # Tu código aquí
    pass

async def main():
    server = await asyncio.start_server(
        manejar_cliente, '127.0.0.1', 9999
    )
    async with server:
        await server.serve_forever()
```

---

### Ejercicio 10: API agregador

**Objetivo:** Crear un programa que consulte múltiples APIs de clima y devuelva el promedio.

**Requisitos:**
1. Consultar al menos 3 APIs de clima diferentes (o usa APIs mock)
2. Extraer temperatura de cada respuesta (formato JSON diferente)
3. Calcular temperatura promedio
4. Si una API falla, usar solo las que funcionaron
5. Timeout de 3 segundos por API

**APIs sugeridas (o usa httpbin para simular):**
- OpenWeatherMap (requiere API key gratuita)
- WeatherAPI (requiere API key gratuita)
- O simula con `https://httpbin.org/json` modificando la respuesta

**Pistas:**
- Usa `asyncio.gather(*tareas, return_exceptions=True)`
- Filtra resultados exitosos vs excepciones
- Maneja JSONs con estructuras diferentes

---

### Ejercicio 11: Download manager con progreso

**Objetivo:** Descargar múltiples archivos grandes mostrando progreso en tiempo real.

**Requisitos:**
1. Descargar 3-5 archivos simultáneamente (usa URLs de archivos grandes de prueba)
2. Mostrar progreso de descarga de cada archivo (porcentaje)
3. Mostrar velocidad de descarga (KB/s)
4. Actualizar display cada 0.5 segundos
5. Usar `asyncio.Queue` para comunicar progreso

**Pistas:**
- Lee chunks con `response.content.read(chunk_size)`
- Usa `asyncio.create_task()` para actualización de progreso en paralelo
- Para display bonito: `\r` para sobrescribir línea en terminal

**Estructura sugerida:**
```python
async def descargar_con_progreso(session, url, nombre, queue):
    # Descarga y reporta progreso
    pass

async def mostrar_progreso(queue, num_descargas):
    # Lee de queue y actualiza display
    pass

async def main():
    archivos = [
        ("http://ipv4.download.thinkbroadband.com/5MB.zip", "archivo1.zip"),
        # Más archivos...
    ]
    # Tu código aquí
```

---

### Ejercicio 12: Base de datos asíncrona

**Objetivo:** Realizar operaciones de base de datos concurrentemente usando `asyncpg` (PostgreSQL) o `motor` (MongoDB).

**Requisitos:**
1. Conectar a una base de datos local
2. Insertar 100 registros concurrentemente (usar `asyncio.gather()`)
3. Realizar 10 queries concurrentes diferentes
4. Calcular tiempo total y comparar con versión síncrona
5. Implementar connection pooling

**Para PostgreSQL (asyncpg):**
```python
import asyncio
import asyncpg

async def insertar_registro(pool, id, nombre):
    async with pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO usuarios(id, nombre) VALUES($1, $2)',
            id, nombre
        )

async def main():
    # Crear connection pool
    pool = await asyncpg.create_pool(
        user='usuario', password='contraseña',
        database='test', host='127.0.0.1'
    )
    
    # Tu código aquí
    
    await pool.close()
```

**Pistas:**
- Connection pool reutiliza conexiones (mucho más eficiente)
- Usa `pool.acquire()` como context manager
- Compara tiempos: 100 inserts secuenciales vs concurrentes

---

## Consejos generales

1. **Debugging asíncrono:** Usa `asyncio.run(main(), debug=True)` para detectar problemas

2. **Evita blocking calls:** Nunca uses `time.sleep()`, `requests.get()`, o file I/O síncrono en código async

3. **Manejo de errores:** Usa `return_exceptions=True` en `gather()` para que una tarea fallida no cancele las demás

4. **Testing:** Prueba con `pytest-asyncio`:
```python
import pytest

@pytest.mark.asyncio
async def test_mi_corrutina():
    resultado = await mi_corrutina()
    assert resultado == "esperado"
```

5. **Profiling:** Usa `asyncio.Task.all_tasks()` para ver qué tareas están corriendo

¡Buena suerte con los ejercicios!