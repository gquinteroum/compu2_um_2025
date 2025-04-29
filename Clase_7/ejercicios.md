## Ejercicios sobre Señales en Sistemas Operativos (Python)

Estos ejercicios están diseñados para afianzar la comprensión y el dominio del sistema de señales en UNIX/POSIX, utilizando Python como lenguaje de implementación. Están ordenados en dificultad progresiva y no repiten los ejemplos presentes en el documento principal.

---

### Ejercicio 1: Manejo básico con `SIGTERM`

**Objetivo:** Familiarizarse con el uso de `SIGTERM` y funciones de limpieza al finalizar un proceso.

**Enunciado:**
Crea un programa que capture la señal `SIGTERM` y, en respuesta, muestre un mensaje de despedida. Asegúrate de registrar una función con `atexit` para que se ejecute al terminar el proceso, independientemente del motivo de finalización.

---

### Ejercicio 2: Diferenciar señales según su origen

**Objetivo:** Comprender cómo múltiples señales pueden ser diferenciadas en un mismo handler.

**Enunciado:**
El proceso principal debe lanzar tres procesos hijos. Cada hijo, luego de un pequeño retardo aleatorio, debe enviar una señal distinta al padre (`SIGUSR1`, `SIGUSR2`, `SIGTERM`). El padre debe manejar todas las señales con un solo handler y registrar cuál hijo envió qué señal, usando `os.getpid()` y `os.getppid()`.

---

### Ejercicio 3: Ignorar señales temporalmente

**Objetivo:** Controlar cuándo un programa debe responder a una señal.

**Enunciado:**
Crea un programa que ignore `SIGINT` (Ctrl+C) durante los primeros 5 segundos de ejecución. Luego, el programa debe restaurar el comportamiento por defecto para esa señal y continuar ejecutando indefinidamente. Verifica que `Ctrl+C` no interrumpe el programa durante los primeros segundos, pero sí lo hace después.

---

### Ejercicio 4: Control multihilo con señales externas

**Objetivo:** Integrar señales con hilos y control de ejecución.

**Enunciado:**
Crea un programa multihilo donde un hilo cuenta regresivamente desde 30. Usa una variable global con `threading.Lock()` para permitir que otro proceso externo, al enviar una señal (`SIGUSR1`), pause la cuenta y otra señal (`SIGUSR2`) la reinicie. El hilo principal debe instalar los handlers y proteger correctamente el estado compartido.

---

### Ejercicio 5: Simulación de cola de trabajos con señales

**Objetivo:** Simular un sistema productor-consumidor asíncrono usando señales.

**Enunciado:**
Desarrolla dos procesos: uno productor y uno consumidor. El productor genera trabajos (simulados por mensajes con timestamp) y, al generarlos, envía `SIGUSR1` al consumidor. El consumidor debe recibir la señal, registrar el timestamp de recepción y "procesar" el trabajo (simulado con un `sleep()`). Implementa una protección contra pérdida de señales: si se reciben varias en rápida sucesión, deben encolarse en una estructura temporal para ser procesadas una por una.

---

Estos ejercicios están pensados para desarrollar dominio práctico del sistema de señales, su integración con procesos e hilos, y las sutilezas de su uso correcto en entornos reales.