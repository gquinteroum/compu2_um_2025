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