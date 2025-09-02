# client_tcp_ipv6.py
import socket

HOST, PORT = "::1", 9301

with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as c:
    c.connect((HOST, PORT, 0, 0))  # flowinfo=0, scopeid=0 para loopback
    c.sendall(b"hola ipv6\n")
    print(c.recv(1024).decode("utf-8", "replace"))