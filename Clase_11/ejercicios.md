# Ejercicios de Programación Concurrente y Procesos en Python y Bash

Estos ejercicios están diseñados para estudiantes de la materia Computación II. Su propósito es consolidar conceptos clave sobre procesos, concurrencia, comunicación entre procesos y manejo de argumentos desde la línea de comandos. Algunos ejercicios están pensados para ser realizados exclusivamente en Python, otros en Bash, y varios integran ambas herramientas.

---

## Ejercicio 1: Creación de Procesos con Argumentos

Escriba un script en Python llamado `gestor.py` que reciba argumentos desde la línea de comandos utilizando `argparse`:

- La opción `--num` indica la cantidad de procesos hijos a crear.
- La opción `--verbose` activa mensajes detallados.

Cada proceso hijo debe dormir entre 1 y 5 segundos y luego terminar. El proceso padre debe imprimir su PID y mostrar la jerarquía de procesos usando `pstree -p`.

Desde otra terminal, el estudiante deberá observar el estado de los procesos con `ps` o accediendo a `/proc`.

---

## Ejercicio 2: Proceso Zombi

Cree un script en Python que genere un proceso hijo que finaliza inmediatamente. El padre no deberá recolectar su estado hasta al menos 10 segundos después.

Desde Bash, utilice `ps` y `/proc/[pid]/status` para identificar el estado Z (zombi) del hijo.

---

## Ejercicio 3: Proceso Huérfano

Diseñe un script que cree un proceso hijo que siga ejecutándose luego de que el proceso padre haya terminado. Verifique desde Bash que el nuevo `PPID` del proceso hijo corresponde a `init` o `systemd`.

---

## Ejercicio 4: Reemplazo con `exec()`

Implemente un script que use `fork()` para crear un proceso hijo. Ese hijo deberá reemplazar su imagen de ejecución por el comando `ls -l` usando `exec()`.

Desde Bash, verifique el reemplazo observando el nombre del proceso con `ps`.

---

## Ejercicio 5: Pipes anónimos entre padre e hijo

Cree un script en Python donde el proceso padre y el hijo se comuniquen usando un `os.pipe()`. El hijo deberá enviar un mensaje al padre, y este deberá imprimirlo por pantalla.

Debe usarse codificación binaria y control adecuado de cierre de descriptores.

---

## Ejercicio 6: FIFO (named pipe) entre dos scripts

Cree un FIFO en `/tmp/mi_fifo` usando Bash (`mkfifo`). Luego:

- Escriba un script `emisor.py` que escriba mensajes en el FIFO.
- Escriba un script `receptor.py` que lea desde el FIFO e imprima los mensajes.

Ejecute ambos scripts en terminales distintas.

---

## Ejercicio 7: Procesos Concurrentes con `multiprocessing`

Utilice `multiprocessing.Process` para crear 4 procesos que escriban su identificador y una marca de tiempo en un mismo archivo de log. Utilice `multiprocessing.Lock` para evitar colisiones.

---

## Ejercicio 8: Condición de Carrera y su Corrección

Implemente un contador compartido entre dos procesos sin usar `Lock`, para evidenciar una condición de carrera. Luego modifique el programa para corregir el problema usando `multiprocessing.Lock`.

Compare ambos resultados.

---

## Ejercicio 9: Control de concurrencia con `Semaphore`

Implemente una versión del problema de los "puestos limitados" usando `multiprocessing.Semaphore`. Cree 10 procesos que intenten acceder a una zona crítica que solo permite 3 accesos simultáneos.

---

## Ejercicio 10: Sincronización con `RLock`

Diseñe una clase `CuentaBancaria` con métodos `depositar` y `retirar`, ambos protegidos con un `RLock`. Permita que estos métodos se llamen recursivamente (desde otros métodos sincronizados).

Simule accesos concurrentes desde varios procesos.

---

## Ejercicio 11: Manejo de Señales

Cree un script que instale un manejador para la señal `SIGUSR1`. El proceso deberá estar en espera pasiva (`pause()` o bucle infinito).

Desde Bash, envíe la señal al proceso con `kill -SIGUSR1 [pid]` y verifique la respuesta.

---

## Ejercicio 12: Ejecución Encadenada con `argparse` y Pipes

Implemente dos scripts:

1. `generador.py`: genera una serie de números aleatorios (parámetro `--n`) y los imprime por salida estándar.
2. `filtro.py`: recibe números por entrada estándar y muestra solo los mayores que un umbral (parámetro `--min`).

Desde Bash, encadene la salida del primero a la entrada del segundo:

```bash
generador.py --n 100 | filtro.py --min 50
```
---

## Ejercicio 13: Visualización de Jerarquía de Procesos

Ejecute un script en Python que cree dos procesos hijos. Desde Bash, utilice `pstree -p` y `ps --forest` para observar la jerarquía. Capture la salida y explique la genealogía de los procesos.

---

## Ejercicio 14: Ejecución Diferida y Sincronización con `sleep`

Cree un script Bash que ejecute en segundo plano un script Python que duerme 10 segundos. Desde otra terminal, verifique su ejecución con `ps`, y envíe una señal para terminarlo prematuramente (`SIGTERM`).

---

## Ejercicio 15: Análisis de Procesos Activos

Desde Bash, cree un script que recorra `/proc` y liste los procesos activos, mostrando para cada uno su PID, PPID, nombre del ejecutable y estado (`cat /proc/[pid]/status`). Genere un resumen con los distintos estados encontrados.

---

## Ejercicio 16: Recolección Manual de Estado de Hijos

Implemente en Python un programa que cree 3 hijos que finalizan en distinto orden. El padre deberá recolectar manualmente cada estado usando `os.waitpid`, y registrar en qué orden terminaron.

---

## Ejercicio 17: Simulación de Lector y Escritor con FIFO

Cree dos scripts Bash: uno que escriba cada segundo en una FIFO y otro que lea continuamente. Analice qué sucede si el lector se lanza antes que el escritor y viceversa.

---

## Ejercicio 18: Observación de Pipes con `lsof`

Ejecute un programa Python que use `os.pipe()` para comunicación entre procesos. Desde Bash, use `lsof -p [pid]` para observar los descriptores de archivo abiertos por el proceso.

---

## Ejercicio 19: Monitoreo de Escritura Concurrente sin Exclusión

Ejecute desde Bash varios procesos Python que escriban a un mismo archivo sin usar `Lock`. Observe y compare el resultado con la versión sincronizada usando `multiprocessing.Lock`.

---

## Ejercicio 20: Interacción entre Procesos con Señales Personalizadas

Implemente dos scripts: uno que espera indefinidamente (`pause`) y otro que envía señales (`SIGUSR1`, `SIGUSR2`) cada cierto tiempo. El receptor deberá reaccionar de forma distinta según la señal recibida.

---
