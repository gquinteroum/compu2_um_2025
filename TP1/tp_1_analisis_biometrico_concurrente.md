# Trabajo Práctico

## "Sistema Concurrente de Análisis Biométrico con Cadena de Bloques Local"

### 0. Objetivo General

Diseñar y programar un sistema distribuido en **procesos** que:

1. **Genere** en tiempo real datos biométricos simulados de una prueba de esfuerzo.
2. **Procese** cada señal en paralelo usando mecanismos de **IPC** y primitivas de **multiprocessing**.
3. **Valide** y **almacene** los resultados en una **cadena de bloques local** para garantizar integridad.

El trabajo se divide en **tres tareas obligatorias** que deberán completarse en orden. No se admite uso de redes ni librerías de aprendizaje automático.

---

### 1. Descripción de la Arquitectura

```
┌─────────────────────────┐                     
│  Proceso Principal      │  1 dato/seg         
│  (generador)            │─────────────┐       
└─────────────────────────┘             │       
        │ pipe/fifo                     │       
        ▼                               ▼       
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Proc A     │  │ Proc B     │  │ Proc C     │
│ Frecuencia │  │ Presión    │  │ Oxígeno    │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │ queue         │ queue         │ queue  
      └───────┬────────┴────────┬──────┘       
              ▼                 ▼              
         ┌─────────────────────────┐           
         │  Proceso Verificador    │           
         └────────┬────────────────┘           
                  │ escribe bloque             
                  ▼                           
         ┌─────────────────────────┐           
         │  Cadena de Bloques      │           
         └─────────────────────────┘           
```

- **Proceso principal**: simula 60 muestras (1 por segundo) con tres campos: `frecuencia`, `presion` (tupla sistólica/diastólica) y `oxigeno` (%).
- **Procesos de análisis** (`Proc A/B/C`): reciben los datos completos, extraen su señal, aplican un cálculo **costoso** (ver Tarea 1) y devuelven un resultado numérico.
- **Proceso verificador**: espera los tres resultados, detecta inconsistencias simples, construye un bloque y lo encadena.
- **Cadena de bloques**: lista enlazada en disco (`blockchain.json`). Cada bloque incluye hash SHA‑256 del anterior.

---

### 2. Requisitos Técnicos Globales

- Código en **Python ≥ 3.9**. Se permite `numpy`, `hashlib`, `multiprocessing`, `queue`, `os`, `json`, `datetime`, `random`.
- Comunicación **Principal → Analizadores**: al menos un `Pipe` o `FIFO` por proceso.
- Comunicación **Analizadores → Verificador**: una `multiprocessing.Queue` por proceso o una cola compartida con tuplas identificadoras.
- Sincronización: `Lock`, `Semaphore` o `Event` donde corresponda.
- El programa principal debe terminar limpiamente (sin zombis ni recursos abiertos).

---

### 3. Tareas Obligatorias

#### **Tarea 1 – Generación y Análisis Concurrente (30 %)**

1. Implemente el **Proceso principal** que, cada segundo, genera un diccionario:
   ```python
   {
       "timestamp": "YYYY-MM-DDTHH:MM:SS",
       "frecuencia": int(60-180),
       "presion": [int(110-180), int(70-110)],
       "oxigeno": int(90-100)
   }
   ```
2. Envíe ese diccionario a los tres procesos analizador mediante IPC.
3. Cada analizador debe:
   - Recibir los 60 paquetes.
   - Mantener una **ventana móvil de los últimos 30 segundos**.
   - Calcular, en cada iteración, **(a)** la media y **(b)** la desviación estándar sobre su señal dentro de la ventana.
4. Enviar un diccionario resultado al verificador:
   ```python
   {
       "tipo": "frecuencia",  # o "presion" / "oxigeno"
       "timestamp": ...,
       "media": ...,
       "desv": ...
   }
   ```

#### **Tarea 2 – Verificación y Construcción de Bloques (35 %)**

1. El **Proceso verificador** debe:
   - Esperar los tres resultados correspondientes al mismo timestamp.
   - Comprobar: `frecuencia < 200`, `90 <= oxigeno <= 100`, presión sistólica < 200.
   - Si algún valor está fuera de rango, marcar el bloque con flag `"alerta": true`.
2. Construir el bloque:
   ```python
   {
       "timestamp": ...,
       "datos": {
           "frecuencia": {"media": ..., "desv": ...},
           "presion": {...},
           "oxigeno": {...}
       },
       "alerta": bool,
       "prev_hash": "...",
       "hash": "sha256(prev_hash + str(datos) + timestamp)"
   }
   ```
3. Encadenar en memoria y **persistir** al archivo `blockchain.json` al finalizar cada segundo.
4. Mostrar por pantalla el índice del bloque, su hash y si contiene alerta.

#### **Tarea 3 – Verificación de Integridad y Reporte (35 %)**

1. Implementar un script externo `verificar_cadena.py` que:
   - Lea `blockchain.json`.
   - Recalcule hashes y verifique encadenamiento.
   - Informe si hay bloques corruptos.
2. Generar un **reporte final** (`reporte.txt`) con:
   - Cantidad total de bloques.
   - Número de bloques con alertas.
   - Promedio general de frecuencia, presión y oxígeno.

---

### 4. Entrega y Evaluación

| Ítem                                                       | Ponderación |
| ---------------------------------------------------------- | ----------- |
| Tarea 1 completada y sin condiciones de carrera            | 30 %        |
| Tarea 2 con encadenamiento correcto y detección de alertas | 35 %        |
| Tarea 3 con verificación íntegra y reporte preciso         | 35 %        |
| Código limpio, documentación y README                      | +10 % bonus |

Debe entregarse:

- Código fuente (.py) y `README.md` con instrucciones de ejecución.
- Archivo `blockchain.json` generado.
- `reporte.txt`.

---

### 5. Reglas y Consejos

- Evitar bucles ocupados: use `sleep(1)` donde corresponda.
- Maneje excepciones y cierre limpio de pipes/queues.
- Aplique buenas prácticas de estilo PEP 8.
