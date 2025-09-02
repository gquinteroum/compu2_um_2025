# client_udp_ipv4.py
import socket

HOST, PORT = "127.0.0.1", 9201

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as c:
    # Enviamos y esperamos respuesta (bloqueante)
    c.sendto(b"ping", (HOST, PORT))
    data, addr = c.recvfrom(4096)
    print(f"< {data!r} desde {addr}")