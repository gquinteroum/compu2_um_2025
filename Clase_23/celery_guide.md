# Celery: Tareas asíncronas distribuidas en producción

## Introducción: Más allá de un solo proceso

Hasta ahora hemos visto herramientas poderosas:
- `asyncio` para concurrencia en un solo proceso
- `concurrent.futures` para paralelismo en una sola máquina

Pero, ¿qué pasa cuando necesitas escalar más allá de una máquina? ¿Qué pasa cuando tienes tareas que:
- Tardan horas en completarse
- Deben ejecutarse en horarios específicos
- Necesitan persistir aunque tu aplicación se caiga
- Deben distribuirse entre múltiples servidores

Entra **Celery**: un sistema de colas de tareas distribuido y asíncrono diseñado para producción.

### La metáfora del restaurante

Imagina un restaurante grande:

**concurrent.futures es como:**
- La cocina del restaurante
- Los chefs trabajan en paralelo
- Pero todo está en un solo lugar
- Si el restaurante cierra, se pierde el trabajo en progreso

**Celery es como:**
- Una cadena de restaurantes con cocinas centralizadas
- Los pedidos se anotan en un sistema central (cola)
- Múltiples cocinas (workers) en diferentes lugares pueden tomar pedidos
- Si una cocina cierra, otras siguen trabajando
- Los pedidos no se pierden, quedan guardados
- Puedes agregar más cocinas según la demanda

### ¿Qué problemas resuelve Celery?

1. **Tareas de larga duración**: Procesar un video de 2 horas sin bloquear tu API
2. **Escalabilidad horizontal**: Agregar más workers sin cambiar código
3. **Resiliencia**: Si un worker muere, otro toma su trabajo
4. **Scheduling**: Ejecutar tareas periódicas (cada hora, cada día)
5. **Persistencia**: Las tareas sobreviven reinicios
6. **Priorización**: Tareas urgentes primero
7. **Monitoreo**: Ver qué está pasando en tiempo real

---

## Arquitectura de Celery

Celery tiene una arquitectura cliente-servidor con tres componentes principales:

### 1. Message Broker (El cartero)

El broker es el sistema que almacena y entrega mensajes entre tu aplicación y los workers. Es el corazón del sistema.

**Opciones populares:**

**RabbitMQ** (Recomendado para producción):
```bash
# Instalar RabbitMQ
docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management
```
- Robusto, maduro, diseñado para mensajería
- Soporta prioridades, routing complejo
- Dashboard web en puerto 15672

**Redis** (Bueno para empezar):
```bash
# Instalar Redis
docker run -d -p 6379:6379 redis
```
- Más simple, fácil de configurar
- También sirve como result backend
- Menos features de mensajería que RabbitMQ

**Comparación:**
| Feature | RabbitMQ | Redis |
|---------|----------|-------|
| Persistencia | Excelente | Buena |
| Velocidad | Rápido | Muy rápido |
| Complejidad | Media | Baja |
| Routing avanzado | ✓ | Limitado |
| Para producción | Ideal | Aceptable |

### 2. Celery Workers (Los trabajadores)

Son procesos Python que ejecutan las tareas. Puedes tener tantos como quieras, en tantas máquinas como quieras.

```bash
# Iniciar un worker
celery -A mi_proyecto worker --loglevel=info

# Iniciar múltiples workers
celery -A mi_proyecto worker --concurrency=4
```

Cada worker:
- Se conecta al broker
- Escucha nuevas tareas
- Las ejecuta cuando llegan
- Reporta resultados

### 3. Result Backend (Opcional, el archivador)

Almacena los resultados de las tareas. Útil si necesitas recuperar el resultado después.

Opciones:
- Redis (más común)
- Base de datos (PostgreSQL, MySQL)
- MongoDB
- Memcached

### El flujo completo

```
Tu App                    Broker                    Workers                 Result Backend
   |                        |                          |                          |
   |-- task.delay(x) ------>|                          |                          |
   |                        |-- pick task ----------->|                          |
   |                        |                          |-- execute task           |
   |                        |                          |-- store result --------->|
   |                        |                          |                          |
   |<-- task.get() --------------------------------------------- retrieve result --|
```

---

## Instalación y configuración básica

### Instalación

```bash
# Celery básico
pip install celery

# Con Redis
pip install celery[redis]

# Con RabbitMQ
pip install celery[amqp]

# Todo incluido
pip install celery[redis,amqp]
```

### Estructura de proyecto básica

```
mi_proyecto/
├── celery_app.py       # Configuración de Celery
├── tasks.py            # Definición de tareas
├── main.py             # Tu aplicación principal
└── celeryconfig.py     # Configuración avanzada (opcional)
```

### Configuración mínima

**celery_app.py:**
```python
from celery import Celery

# Crear instancia de Celery
app = Celery(
    'mi_proyecto',
    broker='redis://localhost:6379/0',      # Dónde está el broker
    backend='redis://localhost:6379/1',     # Dónde guardar resultados
)

# Configuración básica
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Argentina/Mendoza',
    enable_utc=True,
)

# Autodescubrir tareas en módulos
app.autodiscover_tasks(['mi_proyecto'])
```

**tasks.py:**
```python
from celery_app import app
import time

@app.task
def sumar(x, y):
    """Tarea simple"""
    time.sleep(2)  # Simular trabajo
    return x + y

@app.task
def tarea_larga():
    """Tarea que tarda mucho"""
    time.sleep(60)
    return "Terminé después de 1 minuto"
```

**main.py:**
```python
from tasks import sumar, tarea_larga

# Ejecutar tarea de forma asíncrona
result = sumar.delay(4, 6)

# Continuar sin esperar
print("Tarea enviada, continuando...")

# Obtener resultado (esto bloquea hasta que termine)
print(f"Resultado: {result.get(timeout=10)}")
```

### Ejecutar el sistema

```bash
# Terminal 1: Iniciar Redis (si usas Docker)
docker run -d -p 6379:6379 redis

# Terminal 2: Iniciar worker
celery -A celery_app worker --loglevel=info

# Terminal 3: Ejecutar tu aplicación
python main.py
```

---

## Conceptos fundamentales

### 1. Tareas síncronas vs asíncronas

```python
from tasks import sumar

# Forma SÍNCRONA (bloquea hasta terminar)
resultado = sumar(4, 6)
print(resultado)  # 10

# Forma ASÍNCRONA (retorna inmediatamente)
async_result = sumar.delay(4, 6)
print(async_result)  # <AsyncResult: task_id>

# Obtener resultado después
print(async_result.get())  # 10
```

### 2. AsyncResult: El futuro de Celery

Un `AsyncResult` es similar a un `Future` de concurrent.futures:

```python
from tasks import tarea_larga

result = tarea_larga.delay()

# Verificar estado
print(result.ready())    # False (aún corriendo)
print(result.successful())  # None (no terminó)
print(result.failed())   # False

# Esperar con timeout
try:
    valor = result.get(timeout=5)
except TimeoutError:
    print("Tarea tardó más de 5 segundos")

# Sin timeout (espera indefinidamente)
valor = result.get()

# Verificar estado después
print(result.ready())    # True
print(result.successful())  # True si no falló
```

**Estados posibles:**
- `PENDING`: Esperando a ser ejecutada
- `STARTED`: Comenzó a ejecutarse
- `SUCCESS`: Terminó exitosamente
- `FAILURE`: Falló con error
- `RETRY`: Reintentando después de fallo
- `REVOKED`: Cancelada

### 3. Firmas de tareas (Signatures)

Las firmas son una forma de encapsular la invocación de una tarea:

```python
from celery import signature
from tasks import sumar

# Crear firma
sig = signature('tasks.sumar', args=(4, 6))
# O forma corta:
sig = sumar.s(4, 6)

# Ejecutar después
result = sig.delay()
print(result.get())  # 10

# Útil para composición de tareas
```

### 4. Composición de tareas: Chains, Groups, Chords

Celery permite orquestar tareas complejas:

**Chain - Secuencia:**
```python
from celery import chain
from tasks import sumar, multiplicar

# (4 + 6) * 2 = 20
resultado = chain(
    sumar.s(4, 6),
    multiplicar.s(2)  # El resultado del anterior es el primer arg
).apply_async()

print(resultado.get())  # 20
```

**Group - Paralelo:**
```python
from celery import group
from tasks import sumar

# Ejecutar múltiples tareas en paralelo
job = group(
    sumar.s(1, 2),
    sumar.s(3, 4),
    sumar.s(5, 6),
)

result = job.apply_async()
print(result.get())  # [3, 7, 11]
```

**Chord - Paralelo + Callback:**
```python
from celery import chord
from tasks import sumar, sumar_lista

# Ejecutar en paralelo, luego combinar resultados
callback = sumar_lista.s()

resultado = chord([
    sumar.s(1, 2),
    sumar.s(3, 4),
    sumar.s(5, 6),
])(callback)

print(resultado.get())  # 21 (3 + 7 + 11)
```

---

## Ejemplos prácticos resueltos

### Ejemplo 1: Sistema de procesamiento de imágenes

**Escenario:** API web que recibe imágenes, las procesa, y notifica cuando termina.

**celery_app.py:**
```python
from celery import Celery

app = Celery(
    'image_processor',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1',
)

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,  # Tracking de progreso
)
```

**tasks.py:**
```python
from celery_app import app
from PIL import Image, ImageFilter, ImageEnhance
import time
import os

@app.task(bind=True)  # bind=True para acceder a self
def procesar_imagen(self, ruta_imagen, operaciones):
    """
    Procesa una imagen con múltiples operaciones.
    
    Args:
        ruta_imagen: Path a la imagen
        operaciones: Lista de operaciones ['blur', 'rotate', 'resize']
    """
    try:
        # Actualizar estado
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': len(operaciones), 'status': 'Iniciando...'}
        )
        
        img = Image.open(ruta_imagen)
        
        for i, operacion in enumerate(operaciones):
            # Actualizar progreso
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': len(operaciones),
                    'status': f'Aplicando {operacion}...'
                }
            )
            
            if operacion == 'blur':
                img = img.filter(ImageFilter.GaussianBlur(radius=5))
            elif operacion == 'rotate':
                img = img.rotate(90)
            elif operacion == 'resize':
                img = img.resize((800, 600))
            elif operacion == 'enhance':
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
            
            time.sleep(1)  # Simular procesamiento pesado
        
        # Guardar resultado
        output_path = ruta_imagen.replace('.jpg', '_procesada.jpg')
        img.save(output_path)
        
        return {
            'status': 'success',
            'output_path': output_path,
            'operaciones_aplicadas': operaciones
        }
    
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

@app.task
def limpiar_archivos_temporales(edad_dias=7):
    """Tarea de limpieza periódica"""
    import datetime
    
    ahora = datetime.datetime.now()
    archivos_eliminados = 0
    
    for archivo in os.listdir('uploads'):
        ruta = os.path.join('uploads', archivo)
        if os.path.isfile(ruta):
            fecha_creacion = datetime.datetime.fromtimestamp(
                os.path.getctime(ruta)
            )
            
            if (ahora - fecha_creacion).days > edad_dias:
                os.remove(ruta)
                archivos_eliminados += 1
    
    return f"Eliminados {archivos_eliminados} archivos"
```

**api.py (Flask/FastAPI):**
```python
from flask import Flask, request, jsonify
from tasks import procesar_imagen
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_image():
    """Endpoint para subir imagen"""
    file = request.files['image']
    operaciones = request.form.getlist('operaciones')
    
    # Guardar archivo
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)
    
    # Enviar a Celery
    task = procesar_imagen.delay(filepath, operaciones)
    
    return jsonify({
        'task_id': task.id,
        'status': 'processing'
    })

@app.route('/status/<task_id>')
def task_status(task_id):
    """Verificar estado de tarea"""
    task = procesar_imagen.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Esperando...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
```

**Usar el sistema:**
```bash
# Terminal 1: Redis
docker run -d -p 6379:6379 redis

# Terminal 2: Worker
celery -A tasks worker --loglevel=info

# Terminal 3: API
python api.py

# Terminal 4: Test
curl -X POST -F "image=@foto.jpg" \
     -F "operaciones=blur" \
     -F "operaciones=rotate" \
     http://localhost:5000/upload
```

---

### Ejemplo 2: Sistema de envío de emails masivo

**Escenario:** Enviar 10,000 emails sin bloquear la aplicación.

**tasks.py:**
```python
from celery_app import app
from celery import group, chain
import smtplib
from email.mime.text import MIMEText
import time

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_email(self, destinatario, asunto, contenido):
    """
    Envía un email individual con reintentos automáticos
    """
    try:
        # Configuración SMTP (usar tus credenciales reales)
        msg = MIMEText(contenido)
        msg['Subject'] = asunto
        msg['From'] = 'noreply@ejemplo.com'
        msg['To'] = destinatario
        
        # Simular envío (en producción usar SMTP real)
        time.sleep(0.1)
        
        # Simular fallo ocasional para probar reintentos
        import random
        if random.random() < 0.1:
            raise Exception("Error temporal de red")
        
        return {
            'destinatario': destinatario,
            'status': 'enviado',
            'timestamp': time.time()
        }
    
    except Exception as exc:
        # Reintentar automáticamente
        raise self.retry(exc=exc)

@app.task
def enviar_email_batch(destinatarios, asunto, contenido):
    """
    Envía emails a múltiples destinatarios usando group
    """
    # Crear job paralelo
    job = group(
        enviar_email.s(dest, asunto, contenido)
        for dest in destinatarios
    )
    
    result = job.apply_async()
    return f"Enviando {len(destinatarios)} emails..."

@app.task
def generar_reporte_envios(resultados):
    """
    Callback que genera reporte después del envío masivo
    """
    exitosos = sum(1 for r in resultados if r.get('status') == 'enviado')
    fallidos = len(resultados) - exitosos
    
    reporte = {
        'total': len(resultados),
        'exitosos': exitosos,
        'fallidos': fallidos,
        'tasa_exito': exitosos / len(resultados) * 100
    }
    
    # Aquí podrías enviar el reporte por email
    print(f"📊 Reporte: {reporte}")
    
    return reporte

# Uso avanzado: Envío + Reporte
def enviar_campana(destinatarios, asunto, contenido):
    """
    Envía campaña y genera reporte al finalizar usando chord
    """
    from celery import chord
    
    # Tasks paralelas con callback
    callback = generar_reporte_envios.s()
    
    resultado = chord([
        enviar_email.s(dest, asunto, contenido)
        for dest in destinatarios
    ])(callback)
    
    return resultado
```

**main.py:**
```python
from tasks import enviar_campana

# Lista de destinatarios
destinatarios = [f"usuario{i}@ejemplo.com" for i in range(1000)]

# Enviar campaña
resultado = enviar_campana(
    destinatarios,
    asunto="Boletin Semanal",
    contenido="Contenido del email..."
)

print(f"Campaña iniciada: {resultado.id}")

# Esperar resultado del reporte
reporte = resultado.get(timeout=300)  # Timeout de 5 minutos
print(f"Reporte final: {reporte}")
```

---

### Ejemplo 3: Tareas periódicas con Celery Beat

**Escenario:** Tareas que se ejecutan automáticamente en horarios específicos.

**celery_app.py:**
```python
from celery import Celery
from celery.schedules import crontab

app = Celery(
    'periodic_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1',
)

# Configurar tareas periódicas
app.conf.beat_schedule = {
    # Ejecutar cada 30 segundos
    'limpiar-cache-cada-30s': {
        'task': 'tasks.limpiar_cache',
        'schedule': 30.0,
    },
    
    # Ejecutar todos los días a las 2 AM
    'backup-diario': {
        'task': 'tasks.hacer_backup',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Ejecutar cada lunes a las 9 AM
    'reporte-semanal': {
        'task': 'tasks.generar_reporte_semanal',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
    
    # Ejecutar cada hora
    'sincronizar-datos': {
        'task': 'tasks.sincronizar_con_api',
        'schedule': crontab(minute=0),  # Minuto 0 de cada hora
    },
    
    # Ejecutar primer día de cada mes
    'facturacion-mensual': {
        'task': 'tasks.procesar_facturacion',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),
    },
}

app.conf.timezone = 'America/Argentina/Mendoza'
```

**tasks.py:**
```python
from celery_app import app
import datetime
import requests

@app.task
def limpiar_cache():
    """Se ejecuta cada 30 segundos"""
    print(f"🧹 Limpiando cache: {datetime.datetime.now()}")
    # Lógica de limpieza
    return "Cache limpiado"

@app.task
def hacer_backup():
    """Se ejecuta a las 2 AM todos los días"""
    print(f"💾 Iniciando backup: {datetime.datetime.now()}")
    # Lógica de backup
    return "Backup completado"

@app.task
def generar_reporte_semanal():
    """Se ejecuta cada lunes a las 9 AM"""
    print(f"📊 Generando reporte semanal: {datetime.datetime.now()}")
    # Lógica de reporte
    return "Reporte generado"

@app.task
def sincronizar_con_api():
    """Se ejecuta cada hora"""
    print(f"🔄 Sincronizando datos: {datetime.datetime.now()}")
    
    # Ejemplo: obtener datos de API externa
    response = requests.get("https://api.ejemplo.com/datos")
    
    if response.status_code == 200:
        # Procesar y guardar datos
        datos = response.json()
        # Guardar en DB...
        return f"Sincronizados {len(datos)} registros"
    else:
        return "Error en sincronización"

@app.task
def procesar_facturacion():
    """Se ejecuta el primer día de cada mes"""
    print(f"💰 Procesando facturación: {datetime.datetime.now()}")
    # Lógica de facturación
    return "Facturación procesada"
```

**Iniciar el sistema:**
```bash
# Terminal 1: Worker
celery -A celery_app worker --loglevel=info

# Terminal 2: Beat scheduler
celery -A celery_app beat --loglevel=info
```

---

### Ejemplo 4: Rate limiting y control de concurrencia

**Escenario:** Limitar cuántas tareas de cierto tipo se ejecutan simultáneamente.

**celery_app.py:**
```python
from celery import Celery

app = Celery(
    'rate_limited',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1',
)

# Configuración de rate limits
app.conf.update(
    # Límites globales por worker
    worker_prefetch_multiplier=1,  # Tomar 1 tarea a la vez
    task_acks_late=True,  # Confirmar solo después de completar
)
```

**tasks.py:**
```python
from celery_app import app
import time
import requests

@app.task(rate_limit='10/m')  # Máximo 10 por minuto
def llamar_api_externa(url):
    """
    Tarea con rate limit para no sobrecargar API externa
    """
    print(f"🌐 Llamando a {url}")
    response = requests.get(url)
    return response.json()

@app.task(rate_limit='100/h')  # Máximo 100 por hora
def procesar_pago(usuario_id, monto):
    """
    Procesamiento de pagos con límite horario
    """
    print(f"💳 Procesando pago de ${monto} para usuario {usuario_id}")
    time.sleep(2)
    return {"status": "approved", "usuario": usuario_id}

# Control de concurrencia a nivel de cola
@app.task(queue='alta_prioridad')
def tarea_urgente():
    """Tareas urgentes en cola dedicada"""
    pass

@app.task(queue='baja_prioridad')
def tarea_no_urgente():
    """Tareas menos importantes"""
    pass
```

**Configurar workers con diferentes concurrencias:**
```bash
# Worker para tareas urgentes (más threads)
celery -A celery_app worker \
    -Q alta_prioridad \
    --concurrency=10 \
    --loglevel=info

# Worker para tareas no urgentes (menos threads)
celery -A celery_app worker \
    -Q baja_prioridad \
    --concurrency=2 \
    --loglevel=info
```

---

### Ejemplo 5: Manejo avanzado de errores y reintentos

**tasks.py:**
```python
from celery_app import app
from celery.exceptions import Reject
import requests
import time

@app.task(
    bind=True,
    autoretry_for=(requests.RequestException,),  # Reintentar en estos errores
    retry_kwargs={'max_retries': 5},
    retry_backoff=True,  # Backoff exponencial
    retry_backoff_max=600,  # Máximo 10 minutos de espera
    retry_jitter=True,  # Agregar variación aleatoria
)
def descargar_archivo_externo(self, url):
    """
    Descarga con reintentos inteligentes
    """
    try:
        print(f"Intento {self.request.retries + 1} de descargar {url}")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        return {
            'url': url,
            'size': len(response.content),
            'status': 'success'
        }
    
    except requests.RequestException as exc:
        # Celery reintentará automáticamente
        print(f"Error descargando {url}: {exc}")
        raise

@app.task(bind=True, max_retries=3)
def procesar_con_validacion(self, datos):
    """
    Tarea con validación: algunos errores se reintentan, otros no
    """
    try:
        # Validar entrada
        if not datos or 'campo_requerido' not in datos:
            # Error no recuperable, no reintentar
            raise Reject("Datos inválidos", requeue=False)
        
        # Procesamiento que puede fallar temporalmente
        resultado = procesar_datos(datos)
        
        return resultado
    
    except ValueError as exc:
        # Error de validación: no reintentar
        raise Reject(f"Error de validación: {exc}", requeue=False)
    
    except Exception as exc:
        # Error temporal: reintentar con backoff
        countdown = 2 ** self.request.retries  # 2, 4, 8 segundos
        raise self.retry(exc=exc, countdown=countdown)

@app.task(bind=True)
def tarea_con_fallback(self, datos):
    """
    Tarea que ejecuta plan B si falla el plan A
    """
    try:
        # Intentar método principal
        return metodo_principal(datos)
    
    except Exception as exc:
        if self.request.retries < self.max_retries:
            # Reintentar método principal
            raise self.retry(exc=exc)
        else:
            # Después de todos los reintentos, usar fallback
            print("⚠️ Método principal falló, usando fallback")
            return metodo_fallback(datos)

def procesar_datos(datos):
    """Función de procesamiento que puede fallar"""
    time.sleep(1)
    return {"processed": True}

def metodo_principal(datos):
    """Método principal"""
    return {"method": "principal", "datos": datos}

def metodo_fallback(datos):
    """Método alternativo"""
    return {"method": "fallback", "datos": datos}
```

---

## Ejercicios para resolver

### Ejercicio 1: Sistema de notificaciones multi-canal

**Objetivo:** Enviar notificaciones por email, SMS y push simultáneamente.

**Requisitos:**
1. Crear tres tareas: `enviar_email`, `enviar_sms`, `enviar_push`
2. Usar `group` para enviarlas en paralelo
3. Cada canal puede fallar independientemente (simular con random)
4. Tarea callback que registra qué canales funcionaron
5. Rate limit: máximo 100 SMS por minuto

**Estructura sugerida:**
```python
from celery import group, chord
from celery_app import app

@app.task(rate_limit='100/m')
def enviar_sms(telefono, mensaje):
    # Tu código aquí
    pass

@app.task
def enviar_email(email, asunto, contenido):
    # Tu código aquí
    pass

@app.task
def enviar_push(device_id, titulo, mensaje):
    # Tu código aquí
    pass

@app.task
def registrar_resultados(resultados):
    # Analizar qué canales funcionaron
    pass

def notificar_usuario(usuario, mensaje):
    """Notifica por todos los canales disponibles"""
    # Usar chord con group
    pass
```

---

### Ejercicio 2: Pipeline de procesamiento de video

**Objetivo:** Procesar videos en múltiples etapas encadenadas.

**Requisitos:**
1. Etapas: extraer_audio → transcribir → generar_subtitulos → comprimir_video
2. Usar `chain` para ejecutar secuencialmente
3. Cada etapa actualiza progreso con `self.update_state`
4. Si una etapa falla, guardar estado para poder reanudar
5. Estimar tiempo total restante

**Pistas:**
```python
@app.task(bind=True)
def extraer_audio(self, video_path):
    self.update_state(state='PROGRESS', meta={'step': 1, 'total': 4})
    # Usar ffmpeg o similar
    pass

@app.task(bind=True)
def transcribir(self, audio_path):
    # Transcripción con alguna API
    pass

# Crear el pipeline
from celery import chain
pipeline = chain(
    extraer_audio.s(video_path),
    transcribir.s(),
    generar_subtitulos.s(),
    comprimir_video.s()
)
```

---

### Ejercicio 3: Web scraper distribuido con cola de prioridad

**Objetivo:** Scraper que procesa URLs con diferentes prioridades.

**Requisitos:**
1. Tres colas: `urgent`, `normal`, `low`
2. URLs de ciertos dominios van a cola urgente
3. Rate limit por dominio (máximo 10 req/min por dominio)
4. Si una URL falla, bajar su prioridad y reintentar
5. Dashboard que muestre estadísticas en tiempo real

**Estructura:**
```python
@app.task(queue='urgent', rate_limit='10/m')
def scrape_url_urgent(url):
    pass

@app.task(queue='normal')
def scrape_url_normal(url):
    pass

@app.task(queue='low')  
def scrape_url_low(url):
    pass

def clasificar_y_enviar(url):
    """Decide a qué cola enviar según dominio"""
    if 'importante.com' in url:
        return scrape_url_urgent.delay(url)
    # etc
```

---

### Ejercicio 4: Sistema de reportes programados

**Objetivo:** Generar diferentes reportes en horarios específicos usando Celery Beat.

**Requisitos:**
1. Reporte diario de ventas (cada día 8 AM)
2. Reporte semanal de usuarios activos (lunes 9 AM)
3. Reporte mensual financiero (día 1 de cada mes, 10 AM)
4. Cada reporte debe:
   - Consultar base de datos
   - Generar PDF
   - Enviar por email
   - Guardar en carpeta con timestamp
5. Si falla, reintentar 3 veces con 1 hora de diferencia

**Configuración Beat:**
```python
app.conf.beat_schedule = {
    'reporte-diario-ventas': {
        'task': 'tasks.generar_reporte_ventas',
        'schedule': crontab(hour=8, minute=0),
        'kwargs': {'tipo': 'diario'}
    },
    # Agregar más...
}
```

---

### Ejercicio 5: Sistema de caché distribuido con invalidación

**Objetivo:** Cache que se invalida automáticamente y se regenera con Celery.

**Requisitos:**
1. Tarea que calcula datos costosos y los guarda en Redis
2. Tarea periódica (cada 10 minutos) que verifica si hay que actualizar
3. Si los datos fuente cambian, invalidar y recalcular
4. Mientras recalcula, servir datos viejos con warning
5. Logging de todas las actualizaciones

**Estructura:**
```python
import redis

cache = redis.Redis()

@app.task
def calcular_datos_costosos():
    """Cálculo que tarda varios minutos"""
    resultado = realizar_calculos_complejos()
    cache.setex('datos_cache', 600, resultado)  # 10 min TTL
    return resultado

@app.task
def verificar_y_actualizar_cache():
    """Tarea periódica"""
    if necesita_actualizacion():
        calcular_datos_costosos.delay()
```

---

### Ejercicio 6: Workflow complejo con canvas

**Objetivo:** Implementar un workflow de ML: entrenar modelo, evaluar, desplegar.

**Requisitos:**
1. Usar todos los primitivos: chain, group, chord
2. Pipeline:
   - Preparar datos (3 fuentes en paralelo con group)
   - Combinar datasets
   - Entrenar 5 modelos en paralelo
   - Evaluar cada modelo
   - Seleccionar mejor modelo (chord callback)
   - Desplegar a producción
3. Guardar métricas de cada paso
4. Poder cancelar el workflow en cualquier punto

**Estructura:**
```python
from celery import group, chain, chord

# Paso 1: Preparar datos en paralelo
preparacion = group(
    preparar_datos_fuente1.s(),
    preparar_datos_fuente2.s(),
    preparar_datos_fuente3.s(),
)

# Paso 2: Combinar
combinacion = combinar_datasets.s()

# Paso 3: Entrenar modelos en paralelo
entrenamiento = group(
    entrenar_modelo.s('linear'),
    entrenar_modelo.s('rf'),
    entrenar_modelo.s('xgboost'),
    entrenar_modelo.s('neural_net'),
    entrenar_modelo.s('svm'),
)

# Paso 4: Seleccionar mejor
seleccion = seleccionar_mejor_modelo.s()

# Construir workflow completo
workflow = chain(
    preparacion,
    combinacion,
    entrenamiento,
    chord(... )(seleccion),
    desplegar_modelo.s()
)
```

---

## Monitoreo y debugging

### Flower: Dashboard web para Celery

Flower es una herramienta de monitoreo en tiempo real:

```bash
# Instalar
pip install flower

# Ejecutar
celery -A celery_app flower

# Acceder en: http://localhost:5555
```

Features:
- Ver tareas en ejecución
- Estadísticas por worker
- Tasa de éxito/fallo
- Gráficos de throughput
- Controlar workers (restart, shutdown)

### Logging efectivo

```python
import logging
from celery.utils.log import get_task_logger

# Logger específico de Celery
logger = get_task_logger(__name__)

@app.task
def tarea_con_logging():
    logger.info("Tarea iniciada")
    logger.debug("Procesando datos...")
    
    try:
        resultado = procesar()
        logger.info(f"Resultado: {resultado}")
        return resultado
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise
```

### Inspección de workers

```python
from celery_app import app

# Inspeccionar workers activos
inspect = app.control.inspect()

# Ver workers disponibles
print(inspect.active_queues())

# Ver tareas activas
print(inspect.active())

# Ver tareas programadas
print(inspect.scheduled())

# Estadísticas
print(inspect.stats())
```

---

## Mejores prácticas en producción

### 1. Idempotencia

Las tareas deben poder ejecutarse múltiples veces con el mismo resultado:

```python
# ✗ Malo: no idempotente
@app.task
def procesar_pedido(pedido_id):
    pedido = obtener_pedido(pedido_id)
    pedido.estado = 'procesado'
    pedido.save()

# ✓ Bueno: idempotente
@app.task
def procesar_pedido(pedido_id):
    pedido = obtener_pedido(pedido_id)
    if pedido.estado != 'procesado':
        pedido.estado = 'procesado'
        pedido.save()
```

### 2. Timeouts

Siempre configurar timeouts:

```python
@app.task(
    time_limit=300,  # Hard timeout (mata el proceso)
    soft_time_limit=270,  # Soft timeout (lanza excepción)
)
def tarea_con_timeout():
    try:
        # Trabajo que puede tardar
        pass
    except SoftTimeLimitExceeded:
        # Limpieza antes de que se mate el proceso
        cleanup()
        raise
```

### 3. Serialización eficiente

```python
# Configurar serialización
app.conf.update(
    task_serializer='json',  # O 'pickle', 'yaml', 'msgpack'
    result_serializer='json',
    accept_content=['json'],
)

# ✗ Malo: pasar objetos complejos
@app.task
def procesar(objeto_grande):
    pass

# ✓ Bueno: pasar IDs
@app.task
def procesar(objeto_id):
    objeto = cargar_de_db(objeto_id)
    # Procesar
```

### 4. Monitoring y alertas

```python
from celery.signals import task_failure

@task_failure.connect
def handle_task_failure(sender, task_id, exception, **kwargs):
    """Alertar cuando una tarea falla"""
    enviar_alerta_a_equipo(
        f"Tarea {sender.name} falló: {exception}"
    )
```

---

## Conclusión: Cuándo usar Celery

| Escenario | Usar Celery | Alternativa |
|-----------|-------------|-------------|
| Tareas de larga duración | ✅ Sí | - |
| Necesitas scheduling | ✅ Sí | APScheduler (simple) |
| Distribución entre servidores | ✅ Sí | RQ (más simple, solo Redis) |
| Menos de 100 tareas/día | ⚠️ Puede ser overkill | concurrent.futures |
| Real-time crítico (< 1ms) | ❌ No | asyncio |
| Tareas muy simples | ⚠️ Considera alternativas | threading |

**Usa Celery cuando:**
- Necesitas ejecutar tareas fuera del request/response cycle
- Las tareas son CPU o I/O intensive
- Necesitas distribución horizontal
- Quieres scheduling robusto
- Importa la persistencia y resiliencia

¡Ahora tienes el poder de distribuir trabajo a través de múltiples máquinas con Celery!