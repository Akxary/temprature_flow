import struct
from socket import socket
from typing import Sequence


def recieve_signal(client_socket: socket) -> Sequence[float]:
    array_size = int(struct.unpack("!I", client_socket.recv(4))[0])
    expected_length = array_size * 8  # Каждое число занимает 8 байт
    binary_data = b""
    while len(binary_data) < expected_length:
        part = client_socket.recv(expected_length - len(binary_data))
        if not part:
            break
        binary_data += part
    if len(binary_data) == expected_length:
        signals = [float(x) for x in struct.unpack(f"!{array_size}q", binary_data)]
        return signals
    else:
        raise ValueError("Incorrect package size. Expected length: {}, got {}".format(expected_length, len(binary_data)))
    