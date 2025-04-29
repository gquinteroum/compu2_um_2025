## Señales en Sistemas Operativos: Un Mecanismo Asíncrono de Comunicación entre Procesos

### Fundamentos y Teoría Sólida

En los sistemas operativos tipo UNIX, las **señales** representan uno de los mecanismos más antiguos y fundamentales para la comunicación asíncrona entre procesos. Las señales permiten notificar a un proceso sobre la ocurrencia de un evento sin que el proceso deba estar explícitamente esperando dicho evento, introduciendo así un modelo de control reactivo que complementa las estrategias basadas en polling o sincronización activa.

A nivel técnico, una señal es una interrupción software enviada a un proceso por el kernel o por otro proceso. Esta interrupción puede ser el resultado de un evento externo (como una pulsación de teclado), de una condición interna del proceso (como una división por cero), o de la invocación explícita mediante funciones del sistema como `kill()`.

Las señales son un mecanismo de bajo nivel que opera en el espacio del kernel, pero con importantes implicancias en el diseño del espacio de usuario. No son estructuras complejas: cada señal es esencialmente un entero, y su semántica está estandarizada por POSIX. Sin embargo, su integración con el flujo de control, el manejo de recursos compartidos, y la semántica del lenguaje de programación donde se utilicen, exige un entendimiento profundo y preciso.

### Breve Contexto Histórico

Las señales emergen en los primeros sistemas UNIX como una extensión de la semántica de interrupciones. Su objetivo original era proporcionar un mecanismo controlado para gestionar eventos inesperados o excepcionales, tales como la terminación de un hijo o el intento de escritura en un pipe roto. Con el tiempo, su uso se amplió para permitir una comunicación más rica entre procesos, particularmente en scripts y programas de consola.

Con POSIX.1, el modelo de señales fue estandarizado, y se introdujeron señales "reales" (`sigqueue`, `sigaction`, `siginfo_t`) con capacidades más precisas, manejo asíncrono seguro, y la posibilidad de transportar información adicional junto con la señal. A pesar de la proliferación de otros mecanismos IPC, las señales siguen siendo críticas para la gestión de procesos, control de interrupciones, y diseño de sistemas embebidos o de tiempo real.

### Explicación Técnica Avanzada

#### Modelo Conceptual

Cada proceso tiene una *tabla de señales pendientes* y una *máscara de señales bloqueadas*. Cuando se envía una señal, esta se encola (si es posible) en el conjunto de señales pendientes. El kernel inspecciona si la señal está bloqueada: si no lo está, interrumpe el flujo del proceso para ejecutar su manejador (*signal handler*), o en su defecto, aplica la acción por defecto.

Las señales pueden clasificarse en tres tipos fundamentales:
- **Síncronas**: generadas como consecuencia de una acción del propio proceso (ej. `SIGFPE`, `SIGSEGV`).
- **Asíncronas**: generadas desde el exterior (otro proceso, el kernel, o el usuario).
- **Reales (POSIX Real-Time)**: permiten colas múltiples y envío de información adicional (mediante `sigqueue`).

#### Envío de Señales

El envío de señales se puede realizar mediante:
```c
kill(pid_t pid, int sig); // desde otro proceso
raise(int sig);           // desde uno mismo
pthread_kill(pthread_t tid, int sig); // a un hilo específico
sigqueue(pid_t pid, int sig, const union sigval value); // con información
```

#### Manejo de Señales

La instalación de un manejador se realiza mediante `signal()` (no recomendable por su ambigüedad) o `sigaction()`:
```c
#include <signal.h>

void handler(int sig) {
    write(1, "Señal capturada\n", 17);
}

int main() {
    struct sigaction sa = {0};
    sa.sa_handler = handler;
    sigaction(SIGUSR1, &sa, NULL);

    while (1) pause(); // espera señal
}
```

Es fundamental que los manejadores sean *async-signal-safe*, es decir, que sólo utilicen funciones del sistema reentrantes como `write()`, `sigatomic_t`, `exit()`.

#### Bloqueo y Máscaras

Las señales pueden bloquearse selectivamente mediante `sigprocmask()` o `pthread_sigmask()`:
```c
sigset_t mask;
sigemptyset(&mask);
sigaddset(&mask, SIGINT);
pthread_sigmask(SIG_BLOCK, &mask, NULL);
```

Esto es útil cuando una sección crítica no debe ser interrumpida por señales que modifican el estado global.

#### Señales y Hilos

En programas multithreaded, las señales son un terreno especialmente delicado. POSIX define que las señales dirigidas a un proceso pueden ser entregadas a cualquier hilo no bloqueado. Por lo tanto, se suele centralizar el manejo en un solo hilo:
```c
sigwait(&mask, &sig);
```

#### Señales Reales (POSIX)

POSIX introduce señales con colas reales (desde `SIGRTMIN` a `SIGRTMAX`), donde múltiples instancias de la misma señal pueden coexistir, y se puede enviar información adicional como enteros, punteros o estructuras:
```c
sigqueue(pid, SIGRTMIN, (union sigval){.sival_int = 42});
```

El manejador correspondiente accede al dato vía `siginfo_t`.

### Ejemplos en Python

Python tiene un soporte parcial para señales, limitado a procesos principales (no hilos). El módulo `signal` permite registrar manejadores:
```python
import signal
import time

def handler(signum, frame):
    print(f"Recibida señal: {signum}")

signal.signal(signal.SIGUSR1, handler)
print("Esperando señales")
while True:
    time.sleep(1)
```

Enviar con:
```bash
kill -USR1 <pid>
```

### Comparaciones Técnicas

| Mecanismo     | Asíncrono | Bidireccional | Capacidad de Datos | Hilos seguros |
|---------------|-----------|----------------|---------------------|----------------|
| Señales       | ✓         | ✗              | Limitada (excepto sigqueue) | Parcial      |
| Pipes         | ✗         | ✓              | Ilimitada (flujo)   | ✓              |
| Sockets       | ✗         | ✓              | Ilimitada           | ✓              |
| Shared Memory | ✗         | ✓              | Ilimitada           | ✓ (con locks)  |

Las señales son insustituibles en ciertos contextos: notificación de eventos urgentes, interrupciones en programas sin polling, gestión de procesos desde terminales, etc.

### Ejercicios Prácticos

1. **Básico**: Crear un programa que imprima un mensaje al recibir `SIGINT`.
2. **Intermedio**: Registrar múltiples señales con `sigaction()` y proteger secciones críticas con `sigprocmask()`.
3. **Avanzado**: Crear un programa multihilo donde un hilo central recibe señales con `sigwait()` y despacha tareas.

### Ejercicio Resuelto: Sincronización por Señal

Vamos a simular un escenario donde un proceso padre espera a que su hijo realice una inicialización antes de continuar. Utilizaremos `SIGUSR1` como señal de sincronización. El hijo enviará esta señal al padre una vez finalizada la tarea simulada.

```python
import os
import signal
import time
import sys

# Variable global para marcar si se recibió la señal
got_signal = False

def handler(signum, frame):
    global got_signal
    print("[PADRE] Señal recibida, procediendo...")
    got_signal = True

if __name__ == "__main__":
    signal.signal(signal.SIGUSR1, handler)

    pid = os.fork()
    if pid == 0:
        # Proceso hijo
        print("[HIJO] Iniciando inicialización...")
        time.sleep(2)  # Simula inicialización
        os.kill(os.getppid(), signal.SIGUSR1)
        print("[HIJO] Señal enviada al padre")
        sys.exit(0)
    else:
        print("[PADRE] Esperando señal del hijo...")
        while not got_signal:
            time.sleep(0.1)
        print("[PADRE] Continuando con la ejecución")
```

Este ejercicio muestra cómo realizar una sincronización elemental entre procesos utilizando señales en Python. Aunque simple, este patrón es esencial en la construcción de programas reactivos y coordinados.

### Conclusiones y Referencias

Las señales son el canal de comunicación más básico pero profundamente poderoso del sistema operativo. Dominar su semántica permite diseñar software reactivo, eficiente y seguro. Aunque muchas veces eclipsadas por mecanismos de más alto nivel, las señales son insustituibles en el control fino de procesos y sistemas concurrentes.

#### Lecturas y Recursos:
- Kerrisk, M. "The Linux Programming Interface".
- POSIX.1-2017: IEEE Std 1003.1™-2017, sección 2.4 Signals.
- `man 7 signal`, `man 2 sigaction`, `man 2 sigqueue`
- Python Docs: https://docs.python.org/3/library/signal.html

