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