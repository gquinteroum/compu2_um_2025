# Servidor y Cliente con sockets en Python — TCP, UDP, IPv4, IPv6 y dual-stack

**Meta**: construir desde cero (sin socketserver) servidores y clientes con la librería estándar socket: primero TCP/IPv4 muy simple, luego uno un poco más completo (mini-protocolo), después UDP, y finalmente IPv6 y dual-stack (un solo socket que acepta IPv4-mapeado e IPv6, cuando el SO lo permite). Todo con código comentado y notas prácticas.

## 0) Conceptos mínimos

**TCP (SOCK_STREAM)**: flujo confiable, orientado a conexión. Requiere bind → listen → accept → recv/send (server) y connect → recv/send (cliente).

**UDP (SOCK_DGRAM)**: datagramas sin conexión. Server usa bind → recvfrom/sendto. Cliente usa sendto/recvfrom (o connect opcional para fijar destino).

**IPv4 vs IPv6**: AF_INET (tupla (host, port)) vs AF_INET6 (tupla (host, port, flowinfo, scopeid)).

**Dual-stack**: en varios Linux/BSD, un socket IPv6 puede aceptar IPv4-mapeado si IPV6_V6ONLY=0 (depende de la configuración del sistema).

## 1) TCP/IPv4 — Servidor eco simple (secuencial) y su cliente

### Servidor TCP (IPv4) — eco básico

```python
# server_tcp_ipv4_echo.py
import socket

HOST = "127.0.0.1"   # loopback IPv4
PORT = 9101

# 1) Crear socket TCP/IPv4
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)
    print(f"[TCP/IPv4] Escuchando en {HOST}:{PORT} — Ctrl+C para salir")

    try:
        while True:  # servidor secuencial
            conn, addr = srv.accept()
            print("Conexión de", addr)
            with conn:
                # --- ECO POR LÍNEAS SIN makefile() ---
                # TCP es un stream de bytes: podemos recibir trozos parciales.
                # Acumulamos en 'buffer' y vamos extrayendo líneas terminadas en \n.

                buffer = bytearray()
                while True:
                    chunk = conn.recv(4096)   # puede devolver 0..4096 bytes
                    if not chunk:             # 0 bytes = el peer cerró escritura
                        break
                    buffer.extend(chunk)
                    # Procesar todas las líneas completas presentes en el buffer
                    while True:
                        nl = buffer.find(b"\n")
                        if nl == -1:
                            break  # no hay línea completa aún
                        line = buffer[:nl]            # sin el \n

                        # Normalizamos CRLF si hiciera falta (telnet en Windows, etc.)
                        if line.endswith(b"\r"):
                            line = line[:-1]

                        # Respuesta: prefijamos "eco: " y devolvemos con \n
                        resp = b"eco: " + line + b"\n"
                        conn.sendall(resp)

                        # Consumimos la línea + el salto de línea del buffer
                        del buffer[:nl+1]
                print("Cierre de", addr)
    except KeyboardInterrupt:
        print("\nServidor detenido")
```

### 1.b) Servidor TCP (IPv4) — la misma idea pero usando .makefile() (explicado)

A veces es cómodo envolver el socket en un objeto tipo archivo para leer línea a línea sin implementar el buffer manualmente. `conn.makefile("rwb", buffering=0)` crea un file-like en modo binario, lectura/escritura, y sin buffer adicional (el del socket se mantiene). Esto facilita bucles `for raw in f:` que leen hasta EOF cuando el cliente cierra su escritura.

**Ventajas**:
- Código muy legible para protocolos por líneas
- El bucle `for raw in f` termina naturalmente cuando el peer cierra (EOF)

**Precauciones**:
- Es envoltura sobre el socket: hay que cerrar ambos (usando `with conn, conn.makefile(...) as f:` se cierra todo correctamente)
- Si mezclás `conn.recv()` y `f.read()` en el mismo ciclo, podés desincronizar los buffers. Elegí un método por conexión

```python
# server_tcp_ipv4_echo_makefile.py
import socket

HOST = "127.0.0.1"
PORT = 9101

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)
    print(f"[TCP/IPv4 makefile] {HOST}:{PORT}")

    try:
        while True:
            conn, addr = srv.accept()
            print("Conexión de", addr)
            # `makefile("rwb", buffering=0)` → binario, read/write, sin buffer adicional
            with conn, conn.makefile("rwb", buffering=0) as f:
                for raw in f:  # lee línea a línea hasta EOF
                    # 'raw' incluye el salto de línea si vino del peer
                    line = raw.rstrip(b"\r\n")
                    f.write(b"eco: " + line + b"\n")
            print("Cierre de", addr)
    except KeyboardInterrupt:
        print("\nServidor detenido")
```

**¿Cuál usar?** Para ejercicios educativos de framing por líneas, `makefile()` simplifica. Si necesitás control fino de buffers o protocolos binarios con longitud-prefijo, preferí la versión sin `makefile()` (buffer manual).

### Cliente TCP (IPv4)

```python
# client_tcp_ipv4.py
import socket

HOST = "127.0.0.1"
PORT = 9101

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
    c.connect((HOST, PORT))
    for msg in ["hola", "mundo", "fin"]:
        c.sendall((msg + "\n").encode("utf-8"))
    c.shutdown(socket.SHUT_WR)

    buf = []
    while True:
        b = c.recv(4096)
        if not b: 
            break
        buf.append(b)

print(b"".join(buf).decode("utf-8", "replace"))
```

### Variante: uso de makefile para leer por líneas

En Python, un socket es un objeto binario (lee/escribe bytes). Si queremos un manejo más "de archivo de texto" (iterar línea por línea, usar .readline()), podemos envolverlo con `.makefile()`. Esto crea un objeto tipo archivo que se apoya en el socket.

**Ventajas**:
- Iteración directa: `for line in f:` lee hasta `\n`
- Métodos familiares (readline, read, write)
- Se integra con el manejo de buffers de Python

**Precauciones**:
- Cuidado con los buffers dobles (el de makefile y el del socket). Usar `buffering=0` o `flush()` para evitar bloqueos
- Cerrar el makefile también cierra el socket si usamos `with`

## 2) TCP/IPv4 — Servidor medio: mini-protocolo de comandos

Agregamos un pequeño contrato:
- `PING` → `PONG\n`
- `ECHO <texto>` → `<texto>\n`
- `TIME` → `YYYY-mm-dd HH:MM:SS\n`
- Otro → `ERR\n`

### Servidor TCP (IPv4) — mini-protocolo

```python
# server_tcp_ipv4_cmd.py
import socket
import time

HOST, PORT = "127.0.0.1", 9102

def handle(line: str) -> str:
    line = line.strip()
    if line == "PING":
        return "PONG\n"
    if line.startswith("ECHO "):
        return line[5:] + "\n"
    if line == "TIME":
        return time.strftime("%Y-%m-%d %H:%M:%S") + "\n"
    return "ERR\n"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)
    print(f"[TCP/IPv4 CMD] {HOST}:{PORT}")

    try:
        while True:
            conn, addr = srv.accept()
            print("Conexión de", addr)
            with conn, conn.makefile("rwb", buffering=0) as f:
                for raw in f:
                    resp = handle(raw.decode("utf-8", "replace"))
                    f.write(resp.encode("utf-8"))
            print("Cierre de", addr)
    except KeyboardInterrupt:
        print("\nServidor detenido")
```

### Cliente (puede ser el de antes con mensajes distintos)

```python
# client_tcp_cmd.py
import socket

HOST, PORT = "127.0.0.1", 9102

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
    c.connect((HOST, PORT))
    for msg in ["PING", "ECHO hola", "TIME", "FOO"]:
        c.sendall((msg + "\n").encode("utf-8"))
    c.shutdown(socket.SHUT_WR)

    data = []
    while True:
        b = c.recv(1024)
        if not b: 
            break
        data.append(b)

print(b"".join(data).decode("utf-8", "replace"))
```

## 3) UDP/IPv4 — Servidor eco y su cliente

En UDP no hay conexión: cada datagrama trae la dirección de origen. Respondemos al remitente.

### Servidor UDP (IPv4)

```python
# server_udp_ipv4_echo.py
import socket

HOST, PORT = "0.0.0.0", 9201  # 0.0.0.0 = todas las interfaces

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"[UDP/IPv4] {HOST}:{PORT}")
    try:
        while True:
            data, addr = s.recvfrom(4096)  # bloquea hasta recibir
            print(f"{addr} -> {data!r}")
            s.sendto(data, addr)           # eco al remitente
    except KeyboardInterrupt:
        print("\nServidor UDP detenido")
```

### Cliente UDP (IPv4)

```python
# client_udp_ipv4.py
import socket

HOST, PORT = "127.0.0.1", 9201

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as c:
    # Enviamos y esperamos respuesta (bloqueante)
    c.sendto(b"ping", (HOST, PORT))
    data, addr = c.recvfrom(4096)
    print(f"< {data!r} desde {addr}")
```

**Notas UDP**: los datagramas pueden perderse, duplicarse o llegar fuera de orden. Si necesitás garantías, implementá reintentos y lógica de idempotencia en la app o usá TCP.

## 4) TCP/IPv6 — Servidor eco y cliente

Los mismos patrones, pero ahora con `AF_INET6`. Para localhost IPv6 usamos `::1`.

### Servidor TCP (IPv6)

```python
# server_tcp_ipv6_echo.py
import socket

HOST, PORT = "::1", 9301  # loopback IPv6

with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)
    print(f"[TCP/IPv6] [{HOST}]:{PORT}")
    
    try:
        while True:
            conn, addr = srv.accept()  # addr es tupla IPv6 (ip, port, flowinfo, scopeid)
            print("Conexión de", addr)
            with conn:
                while True:
                    b = conn.recv(4096)
                    if not b: 
                        break
                    conn.sendall(b)
            print("Cierre de", addr)
    except KeyboardInterrupt:
        print("\nServidor IPv6 detenido")
```

### Cliente TCP (IPv6)

```python
# client_tcp_ipv6.py
import socket

HOST, PORT = "::1", 9301

with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as c:
    c.connect((HOST, PORT, 0, 0))  # flowinfo=0, scopeid=0 para loopback
    c.sendall(b"hola ipv6\n")
    print(c.recv(1024).decode("utf-8", "replace"))
```

**Tip**: si querés escribir código portátil para IPv4/IPv6, usá `socket.getaddrinfo(host, port, type=SOCK_STREAM)` y probá conexiones en orden.

## 5) TCP dual-stack (cuando el SO lo permite)

Un socket IPv6 puede aceptar tráfico IPv6 y también IPv4-mapeado (`::ffff:a.b.c.d`) si `IPV6_V6ONLY=0`. En Linux moderno suele venir activado por defecto (permitiendo IPv4-mapeado), pero algunos sistemas lo fuerzan a 1. Lo configuramos explícitamente:

### Servidor TCP dual-stack

```python
# server_tcp_dualstack.py
import socket

HOST6, PORT = "::", 9401  # todas las interfaces IPv6; con dual-stack aceptará IPv4-mapeado

with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Desactivar V6 only → permitir IPv4-mapeado si el kernel lo soporta
    try:
        srv.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        print("Dual-stack habilitado")
    except OSError as e:
        # El sistema podría no permitir cambiarlo: seguirá solo IPv6
        print(f"Advertencia: No se pudo habilitar dual-stack: {e}")

    srv.bind((HOST6, PORT))
    srv.listen(16)
    print(f"[TCP dual-stack] [{HOST6}]:{PORT} — acepta ::1 y (si habilitado) 127.0.0.1 via mapeo")

    try:
        while True:
            conn, addr = srv.accept()
            # addr[0] podría ser IPv6 real o IPv4-mapeado (p. ej., ::ffff:127.0.0.1)
            print("Conexión de", addr)
            with conn:
                conn.sendall(b"hola dual\n")
    except KeyboardInterrupt:
        print("\nServidor dual-stack detenido")
```

### Cliente IPv4 e IPv6 contra el dual-stack

```python
# client_dualstack.py
import socket

PORT = 9401

# Cliente IPv4
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c4:
        c4.connect(("127.0.0.1", PORT))
        print("IPv4:", c4.recv(1024).decode("utf-8", "replace"))
except Exception as e:
    print(f"Error IPv4: {e}")

# Cliente IPv6
try:
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as c6:
        c6.connect(("::1", PORT, 0, 0))
        print("IPv6:", c6.recv(1024).decode("utf-8", "replace"))
except Exception as e:
    print(f"Error IPv6: {e}")
```

**Importante**: si tu kernel/seteo de red fuerza `IPV6_V6ONLY=1`, el servidor anterior será solo IPv6. En ese caso, mantené dos sockets: uno `AF_INET` y otro `AF_INET6` (doble bind/listen/accept).

## 6) Apéndice: patrón de lectura robusta (TCP)

Para flujos largos, conviene un bucle de lectura que acumule hasta condición de fin (peer cierra o llegamos a la longitud esperada):

```python
def recv_all(sock, nbytes=None, chunk=65536):
    """Lee hasta EOF o hasta nbytes si se especifica."""
    parts = []
    total = 0
    while True:
        try:
            b = sock.recv(min(chunk, nbytes - total) if nbytes else chunk)
            if not b:
                break
            parts.append(b)
            total += len(b)
            if nbytes is not None and total >= nbytes:
                break
        except socket.error:
            break
    return b"".join(parts)
```