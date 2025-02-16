from pathlib import Path
import socket
import struct
from typing import Sequence

import pandas as pd

def send_signal(host: str, port: int, signals: Sequence[int])->None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    try:
        # Отправка размера массива (4 байта)
        array_size = len(signals)
        client_socket.sendall(struct.pack("!I", array_size))
        # Отправка данных
        client_socket.sendall(struct.pack(f"!{array_size}d", *signals))
    finally:
        client_socket.close()

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 8585
    # path = Path(r"D:\YandexDisk\Актуал\SC_UI\2025-02-12_spiral_lamp\u_2.199_exp_16.704_4_400_1120_14765_1.csv")
    # path = Path(r"D:\YandexDisk\Актуал\SC_UI\2025-02-12_spiral_lamp\u_4.499_exp_16.704_4_400_1120_14765_0.csv")
    path = Path(r"D:\YandexDisk\Актуал\SC_UI\2025-02-12_spiral_lamp\u_6.499_exp_16.704_4_400_1120_14765_0.csv")
    signals = pd.read_csv(path, skiprows=1, header=None, decimal=",")[[5]].to_numpy()
    #[1, 2, 3, 4, 5]
    send_signal(HOST, PORT, [*signals])
    