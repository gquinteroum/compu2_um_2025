# Prácticas de Sockets — Clientes TCP/UDP, Servidores Secuenciales y Bonus AF_UNIX

> **Objetivo general.** Aprender (y practicar) la construcción de **clientes TCP/UDP en Internet** usando `netcat` como servidor, luego implementar **servidores secuenciales** (sin concurrencia) reutilizando nuestros clientes, y finalmente un **bonus AF_UNIX** con trucos avanzados (SO_PEERCRED y SCM_RIGHTS). Todos los ejemplos son en **Python 3** y están **comentados**.

---

## Preludio — AF_UNIX (local)

### 1) Cliente UDS STREAM (eco local)
**Idea.** Igual que TCP, pero todo local: `AF_UNIX/SOCK_STREAM`. Sirve de calentamiento para familiarizarnos con la API.

**Servidor (netcat):**
```bash
nc -lU /tmp/eco.sock
```
> Escribir algo en el cliente y verificar que el servidor lo reciba (y responda si tecleás desde `nc`).

**Cliente (Python):**
```python
import socket
import os

SOCKET_PATH = "/tmp/eco.sock"

def main():
    if not os.path.exists(SOCKET_PATH):
        raise SystemExit(f"No existe {SOCKET_PATH}. ¿Arrancaste `nc -lU {SOCKET_PATH}`?")

    # AF_UNIX = dominio local (archivo-socket), STREAM = estilo TCP
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(SOCKET_PATH)
        s.sendall(b"hola desde UDS\n")
        # `nc` no hace eco automático, pero podés teclear algo y ENTER en la terminal del nc
        # para que el cliente lo lea. Si no hay datos, recv puede bloquear.
        data = s.recv(4096)
        print(f"< {data!r}")

if __name__ == "__main__":
    main()
```

---

## Nivel 1 — Clientes Internet (TCP/UDP) usando `netcat` como servidor

### 2) Cliente TCP “hola mundo” (bloqueante)
**Idea.** Conectarse a `127.0.0.1:9001`, enviar texto, leer respuesta, cerrar.

**Servidor (netcat):**
```bash
nc -l 127.0.0.1 9001
```

**Cliente (Python):**
```python
import socket

def main():
    HOST, PORT = "127.0.0.1", 9001
    # AF_INET = IPv4, SOCK_STREAM = TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))                # 3-way handshake TCP
        s.sendall(b"hola mundo\n")            # envío atómico (o en fragmentos internos)
        data = s.recv(4096)                    # bloquea hasta recibir algo o cerrar
        print(f"< {data!r}")

if __name__ == "__main__":
    main()
```

---

### 3) Cliente TCP por líneas (framing con `\n`)
**Idea.** En TCP no existen “mensajes” delimitados: hay que decidir un **framing**. Aquí, por líneas.

**Servidor (netcat):**
```bash
nc -l 127.0.0.1 9002
```

**Cliente (Python):**
```python
import socket

def send_lines(sock, lines):
    for line in lines:
        if not line.endswith("\n"):
            line += "\n"
        sock.sendall(line.encode("utf-8"))

def recv_until_closed(sock):
    # Acumula hasta que el peer cierre; en un protocolo real pararíamos por un token/longitud
    chunks = []
    while True:
        b = sock.recv(1024)
        if not b:  # 0 bytes → peer cerró
            break
        chunks.append(b)
    return b"".join(chunks)

def main():
    HOST, PORT = "127.0.0.1", 9002
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        send_lines(s, ["uno", "dos", "tres"])  # desde la terminal del `nc` podés escribir respuestas
        s.shutdown(socket.SHUT_WR)               # anuncias que ya no enviarás más
        data = recv_until_closed(s)
        print(data.decode("utf-8", errors="replace"))

if __name__ == "__main__":
    main()
```

---

### 4) Cliente TCP con lecturas parciales
**Idea.** Leer **payloads grandes** en bucle hasta que el peer cierre. Importa para archivos o mensajes largos.

**Servidor (netcat):**
```bash
nc -l 127.0.0.1 9003 < archivo_grande.bin
```

**Cliente (Python):**
```python
import socket

def recv_all(sock):
    chunks = []
    while True:
        b = sock.recv(64 * 1024)  # 64 KiB por iteración
        if not b:
            break
        chunks.append(b)
    return b"".join(chunks)

def main():
    HOST, PORT = "127.0.0.1", 9003
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        data = recv_all(s)
        print(f"Recibidos {len(data)} bytes")

if __name__ == "__main__":
    main()
```

---

### 5) Cliente TCP con timeouts y reintentos
**Idea.** Manejar servidores que responden lento o aún no están arriba.

**Servidor (netcat):**
```bash
# Arrancarlo más tarde para forzar reintentos
nc -l 127.0.0.1 9004
```

**Cliente (Python):**
```python
import socket
import time

HOST, PORT = "127.0.0.1", 9004

def try_connect(max_retries=5, base_backoff=0.5):
    for attempt in range(1, max_retries + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.5)  # segundos
                s.connect((HOST, PORT))
                s.sendall(b"ping\n")
                data = s.recv(1024)
                return data
        except (socket.timeout, ConnectionRefusedError) as e:
            sleep_s = base_backoff * attempt
            print(f"Intento {attempt} falló ({e}). Reintento en {sleep_s:.1f}s...")
            time.sleep(sleep_s)
    raise TimeoutError("Servidor no disponible tras varios reintentos")

if __name__ == "__main__":
    print(try_connect())
```

---

### 6) Cliente TCP con `getaddrinfo` (IPv4/IPv6)
**Idea.** Resolver múltiples familias y conectarse a la primera que funcione.

**Servidor (netcat):**
```bash
# IPv4
nc -l 0.0.0.0 9005
# (Opcional) IPv6 si tu nc lo soporta
# nc -6 -l :: 9005
```

**Cliente (Python):**
```python
import socket

def connect_first(host, port):
    # getaddrinfo devuelve posibles (familia, tipo, protocolo, canonname, sockaddr)
    for fam, stype, proto, _canon, sockaddr in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM):
        try:
            with socket.socket(fam, stype, proto) as s:
                s.connect(sockaddr)
                s.sendall(b"hola\n")
                return s.recv(1024)
        except OSError:
            continue
    raise OSError("No se pudo conectar en ninguna familia/dirección")

if __name__ == "__main__":
    print(connect_first("localhost", 9005))
```

---

### 7) Cliente UDP “ping-pong” manual
**Idea.** UDP es datagramas: no hay conexión ni stream. Enviar/recibir con `sendto/recvfrom`.

**Servidor (netcat):**
```bash
nc -u -l 127.0.0.1 9006
# Escribir respuesta manual “pong” cuando el cliente envíe “ping”
```

**Cliente (Python):**
```python
import socket

HOST, PORT = "127.0.0.1", 9006

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(b"ping", (HOST, PORT))
    data, addr = s.recvfrom(2048)
    print(f"< {data!r} desde {addr}")
```

---

### 8) Cliente UDP con timeout + retransmisión
**Idea.** UDP puede perder paquetes. Implementamos reintentos con timeout.

**Servidor (netcat):**
```bash
nc -u -l 127.0.0.1 9007
```

**Cliente (Python):**
```python
import socket

HOST, PORT = "127.0.0.1", 9007

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.settimeout(1.0)
    retries = 3
    for i in range(1, retries + 1):
        try:
            s.sendto(b"TIME", (HOST, PORT))
            data, _ = s.recvfrom(2048)
            print("Respuesta:", data.decode())
            break
        except socket.timeout:
            print(f"Timeout intento {i}; reintentando...")
    else:
        print("Sin respuesta tras reintentos")
```

---

### 9) Cliente UDP broadcast (discovery)
**Idea.** Enviar a broadcast para descubrir servicios en la red local.

**Servidor (netcat):**
```bash
# Escuchar en todas las interfaces
nc -u -l 0.0.0.0 9008
```

**Cliente (Python):**
```python
import socket

PORT = 9008
BROADCAST = ("255.255.255.255", PORT)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(1.0)
    s.sendto(b"DISCOVER?", BROADCAST)
    try:
        data, addr = s.recvfrom(4096)
        print(f"{addr} -> {data!r}")
    except socket.timeout:
        print("Nadie respondió al broadcast (o la red lo filtra)")
```

---

## Nivel 2 — Servidores Internet (sin concurrencia) usando nuestros clientes (y `nc`)

### 10) Servidor TCP eco (secuencial)
**Idea.** Atender **una conexión por vez** y luego volver a `accept()`. Útil para entender el ciclo de vida sin concurrencia.

**Cliente:** ejercicio #2 o `nc 127.0.0.1 9010`

**Servidor (Python):**
```python
import socket

HOST, PORT = "127.0.0.1", 9010

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)  # backlog
    print(f"Escuchando en {HOST}:{PORT} ... Ctrl+C para salir")

    while True:  # loop de sesiones (secuenciales)
        conn, addr = srv.accept()
        print("Conexión de", addr)
        with conn:
            while True:
                b = conn.recv(4096)
                if not b:
                    break  # peer cerró
                conn.sendall(b)  # eco
        print("Cierre de", addr)
```

---

### 11) Servidor TCP por líneas con comandos
**Idea.** Implementar un mini-protocolo textual: `PING`→`PONG`, `ECHO <msg>`, `TIME`.

**Cliente:** #3 o `nc 127.0.0.1 9011`

**Servidor (Python):**
```python
import socket
import time

HOST, PORT = "127.0.0.1", 9011

def handle_line(line: str) -> str:
    line = line.strip()
    if line == "PING":
        return "PONG\n"
    if line.startswith("ECHO "):
        return line[5:] + "\n"
    if line == "TIME":
        return time.strftime("%Y-%m-%d %H:%M:%S") + "\n"
    return "ERR desconocido\n"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)
    print(f"CMD en {HOST}:{PORT}")

    while True:
        conn, addr = srv.accept()
        with conn, conn.makefile("rwb", buffering=0) as f:
            for raw in f:  # itera por líneas (bloqueante)
                resp = handle_line(raw.decode("utf-8", "replace"))
                f.write(resp.encode("utf-8"))
```

---

### 12) Servidor TCP con timeout de inactividad
**Idea.** Cerrar conexiones “colgadas” para liberar recursos.

**Cliente:** #2/#3 o `nc 127.0.0.1 9012`

**Servidor (Python):**
```python
import socket

HOST, PORT = "127.0.0.1", 9012
IDLE_TIMEOUT = 10  # segundos

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)
    print(f"Timeout server en {HOST}:{PORT} (IDLE={IDLE_TIMEOUT}s)")

    while True:
        conn, addr = srv.accept()
        with conn:
            conn.settimeout(IDLE_TIMEOUT)
            try:
                while True:
                    b = conn.recv(4096)
                    if not b:
                        break
                    conn.sendall(b)
            except socket.timeout:
                print("Inactividad excedida para", addr)
                # cierre implícito al salir del with
```

---

### 13) Servidor UDP eco
**Idea.** Responder al remitente con lo mismo que envía; no hay conexiones.

**Cliente:** #7 o `nc -u 127.0.0.1 9013`

**Servidor (Python):**
```python
import socket

HOST, PORT = "0.0.0.0", 9013

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"UDP eco en {HOST}:{PORT}")
    while True:
        data, addr = s.recvfrom(4096)
        print(f"{addr} -> {data!r}")
        s.sendto(data, addr)
```

---

### 14) Servidor UDP “TIME”
**Idea.** Si recibe `TIME`, responde la hora; en otro caso contesta `ERR`.

**Cliente:** #8 o `nc -u 127.0.0.1 9014`

**Servidor (Python):**
```python
import socket
import time

HOST, PORT = "0.0.0.0", 9014

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"UDP TIME en {HOST}:{PORT}")
    while True:
        data, addr = s.recvfrom(2048)
        msg = data.decode("utf-8", "replace").strip()
        if msg == "TIME":
            s.sendto(time.strftime("%H:%M:%S").encode(), addr)
        else:
            s.sendto(b"ERR\n", addr)
```

---

## Bonus AF_UNIX — UDS avanzados (local)

> **Nota.** Estos ejercicios son locales y opcionales. Complementan la práctica con conceptos potentes del mundo Unix.

### B1) UDS DATAGRAM (eco local)
**Idea.** Como UDP pero local y confiable. Usa `sendto/recvfrom` con rutas de archivo.

**Servidor (Python):**
```python
import socket, os
SRV = "/tmp/uds_dgram_srv"

try: os.unlink(SRV)
except FileNotFoundError: pass

with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as s:
    s.bind(SRV)
    print("UDS-DGRAM listo", SRV)
    while True:
        data, addr = s.recvfrom(2048)  # addr es la ruta del cliente
        s.sendto(data, addr)
```

**Cliente (Python):**
```python
import socket, os
SRV = "/tmp/uds_dgram_srv"
CLI = "/tmp/uds_dgram_cli"

try: os.unlink(CLI)
except FileNotFoundError: pass

with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as c:
    c.bind(CLI)               # en DGRAM local, cada lado suele tener su path
    c.sendto(b"hola", SRV)
    data, _ = c.recvfrom(2048)
    print(data)
```

---

### B2) Abstract namespace (Linux)
**Idea.** Sockets sin archivo en disco. El nombre empieza con `\0` (byte nulo).

**Servidor (Python, Linux):**
```python
import socket

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.bind("\0demo_abstract")  # no crea archivo en /tmp
    s.listen(1)
    conn, _ = s.accept()
    with conn:
        conn.sendall(b"hola abstract\n")
```

**Cliente (Python):**
```python
import socket
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
    c.connect("\0demo_abstract")
    print(c.recv(1024))
```

---

### B3) SO_PEERCRED — obtener UID/GID/PID del peer
**Idea.** El servidor puede conocer credenciales del cliente (Linux) sin autenticación adicional. Útil para CLIs locales.

**Servidor (Python, Linux):**
```python
import socket, struct, os

SO_PEERCRED = 17  # en Linux
fmt = "iii"       # pid, uid, gid

SRV = "/tmp/peercd.sock"
try: os.unlink(SRV)
except FileNotFoundError: pass

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.bind(SRV)
    s.listen(1)
    conn, _ = s.accept()
    with conn:
        pid, uid, gid = struct.unpack(fmt, conn.getsockopt(socket.SOL_SOCKET, SO_PEERCRED, struct.calcsize(fmt)))
        print({"pid": pid, "uid": uid, "gid": gid})
        conn.sendall(f"Hola UID={uid} PID={pid}\n".encode())
```

**Cliente (Python):**
```python
import socket
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
    c.connect("/tmp/peercd.sock")
    print(c.recv(1024))
```

---

### B4) SCM_RIGHTS — pasar descriptores de archivo entre procesos
**Idea.** Un proceso puede “prestar” un **descriptor** (p. ej., un archivo ya abierto) a otro proceso a través de UDS. “Superpoder” de Unix.

**Servidor (envía FD):**
```python
import socket, os, array
SRV = "/tmp/fdpass.sock"
try: os.unlink(SRV)
except FileNotFoundError: pass

# Prepara un archivo a compartir
fd_to_share = os.open("/etc/hostname", os.O_RDONLY)

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.bind(SRV)
    s.listen(1)
    conn, _ = s.accept()
    with conn:
        # Prepara mensaje de control con el FD
        fds = array.array("i", [fd_to_share])
        anc = [(socket.SOL_SOCKET, socket.SCM_RIGHTS, fds.tobytes())]
        conn.sendmsg([b"FD"], anc)  # el payload de datos es arbitrario

os.close(fd_to_share)
```

**Cliente (recibe FD):**
```python
import socket, array, os

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
    c.connect("/tmp/fdpass.sock")
    # Recibir con buffer para ancillary data
    fds = array.array("i")
    msg, anc, flags, addr = c.recvmsg(1024, socket.CMSG_SPACE(array.array("i", [0]).itemsize))
    for level, ctype, data in anc:
        if level == socket.SOL_SOCKET and ctype == socket.SCM_RIGHTS:
            fds.frombytes(data[:fds.itemsize])
    if not fds:
        raise SystemExit("No llegó ningún FD")

    borrowed_fd = fds[0]
    # Leer del descriptor recibido (como si lo hubiéramos abierto aquí)
    os.lseek(borrowed_fd, 0, os.SEEK_SET)
    print(os.read(borrowed_fd, 4096).decode(errors="replace"))
    os.close(borrowed_fd)
```

---

## Cierre — Qué aprendiste y cómo seguir

- **Clientes TCP/UDP (Internet):** dominás `connect/send/recv` (stream) y `sendto/recvfrom` (datagramas), más **timeouts**, **reintentos** y **framing** por líneas.
- **Servidores secuenciales:** comprendiste el **ciclo de vida** `bind → listen → accept → recv/send → close` (TCP) y el modelo sin conexión en UDP.
- **Bonus AF_UNIX:** viste capacidades locales potentes (UDS DATAGRAM, abstract namespace, **SO_PEERCRED** para credenciales y **SCM_RIGHTS** para pasar descriptores).

