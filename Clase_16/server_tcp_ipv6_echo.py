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