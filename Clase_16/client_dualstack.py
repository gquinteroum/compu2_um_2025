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