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