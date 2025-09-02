# socket_utils.py
import socket

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