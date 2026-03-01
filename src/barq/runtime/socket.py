import socket


class SocketReader:
    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.buffer = bytearray()

    def readline(self) -> str:
        while True:
            idx = self.buffer.find(b"\r\n")
            if idx != -1:
                line = self.buffer[:idx].decode("latin-1")
                del self.buffer[:idx + 2]
                return line
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("Disconnected")
            self.buffer.extend(chunk)

    def read(self, n: int) -> bytes:
        while len(self.buffer) < n:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("Disconnected")
            self.buffer.extend(chunk)
        data = bytes(self.buffer[:n])
        del self.buffer[:n]
        return data
