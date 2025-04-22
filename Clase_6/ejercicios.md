## Ejercicios prácticos sobre FIFOs en Unix/Linux (sin repetir ejemplos del documento)

Estos ejercicios están diseñados para estudiantes de tercer año de Ingeniería en Informática, como parte del módulo de IPC (Inter-Process Communication). Todos deben resolverse utilizando Python sobre un sistema Unix/Linux.

---

### Ejercicio 1 — Lectura diferida
**Objetivo**: Comprender el bloqueo de lectura en un FIFO.

**Instrucciones**:
1. Crear un FIFO llamado `/tmp/test_fifo`.
2. Ejecutar un script Python que intente leer desde el FIFO antes de que exista un escritor.
3. En otro terminal, ejecutar un script que escriba un mensaje en el FIFO.

**Preguntas**:
- ¿Qué se observa en el lector mientras espera?
- ¿Qué ocurre si se escriben múltiples líneas desde el escritor?

---

### Ejercicio 2 — FIFO como buffer entre procesos
**Objetivo**: Simular un flujo de datos continuo entre dos procesos.

**Instrucciones**:
1. Crear un proceso productor que escriba números del 1 al 100 en el FIFO con un `sleep(0.1)`.
2. Crear un consumidor que lea esos números del FIFO y los imprima con su timestamp local.
3. Asegurarse de que ambos scripts se ejecuten en paralelo.

**Extensión**: Agregar lógica en el consumidor para detectar si falta un número (por ejemplo, si no es consecutivo).

---

### Ejercicio 3 — FIFO + archivos
**Objetivo**: Usar un FIFO como entrada para un proceso que guarda datos en un archivo.

**Instrucciones**:
1. Crear un script que escuche un FIFO y guarde todo lo que llega en `output.txt`.
2. Otro script debe leer líneas desde el teclado y enviarlas al FIFO.
3. Al escribir "exit" se debe cerrar todo correctamente.

---

### Ejercicio 4 — Múltiples productores
**Objetivo**: Estudiar el comportamiento de múltiples escritores sobre un mismo FIFO.

**Instrucciones**:
1. Crear un FIFO `/tmp/fifo_multi`.
2. Ejecutar tres scripts distintos que escriban mensajes periódicamente (por ejemplo, "Soy productor 1", etc.).
3. Un solo lector debe mostrar los mensajes.

**Reflexión**: ¿Qué pasa si todos escriben al mismo tiempo? ¿Hay mezcla de líneas? ¿Es atómico?

---

### Ejercicio 5 — FIFO con apertura condicional
**Objetivo**: Usar `os.open()` y manejar errores.

**Instrucciones**:
1. Usar `os.open()` con flags como `O_NONBLOCK`.
2. Crear un lector que intente abrir el FIFO sin bloquear.
3. Si el FIFO no tiene escritores, debe imprimir un mensaje y salir correctamente.

**Desafío adicional**: Hacer que el lector reintente 5 veces con espera entre intentos antes de salir.

---

### Ejercicio 6 — Chat asincrónico con doble FIFO
**Objetivo**: Crear una estructura de comunicación bidireccional entre dos usuarios.

**Instrucciones**:
1. Crear dos FIFOs: `/tmp/chat_a` y `/tmp/chat_b`.
2. Usuario A escribe en `chat_a` y lee de `chat_b`, y viceversa.
3. Implementar dos scripts simétricos, uno para cada usuario.

**Extras**:
- Permitir comandos como `/exit` para salir.
- Mostrar los mensajes con nombre de emisor y timestamp.

---

### Ejercicio 7 — Monitor de temperatura simulado
**Objetivo**: Simular un sensor que envía datos por FIFO y un visualizador que los muestra.

**Instrucciones**:
1. Script A (simulador): cada segundo escribe en el FIFO una temperatura aleatoria entre 20 y 30.
2. Script B (monitor): lee las temperaturas y muestra alertas si superan los 28 grados.

**Variante**: Agregar un log con fecha y hora.

---

**Recomendación para todos los ejercicios**:
Utilizar `mkfifo()` o el comando shell `mkfifo`, y eliminar el FIFO con `os.remove()` o `rm` al final de cada script para evitar errores futuros.

---

Reflexionar no solo sobre el funcionamiento técnico, sino sobre cómo estas estructuras permiten modelar arquitecturas de software robustas, modulares y concurrentes.

