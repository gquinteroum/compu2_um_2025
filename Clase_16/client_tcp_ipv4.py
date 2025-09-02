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