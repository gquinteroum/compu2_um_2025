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