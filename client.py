from pathlib import Path
import socket
import struct
from time import sleep
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
        client_socket.sendall(struct.pack(f"!{array_size}l", *signals))
    finally:
        client_socket.close()

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 8585
    # path = Path(r"D:\YandexDisk\Актуал\SC_UI\2025-02-12_spiral_lamp\u_2.199_exp_16.704_4_400_1120_14765_1.csv")
    # path = Path(r"D:\YandexDisk\Актуал\SC_UI\2025-02-12_spiral_lamp\u_4.499_exp_16.704_4_400_1120_14765_0.csv")
    # path = Path(r"D:\YandexDisk\Актуал\SC_UI\2025-02-12_spiral_lamp\u_6.499_exp_16.704_4_400_1120_14765_0.csv")
    # signals = [int(x) for x in pd.read_csv(path, skiprows=1, header=None, decimal=",")[5].to_list()]
    # path = Path(r"D:\Downloads\2024-10-30_spiral_lamp\u_3.499_exp_16.704_3_560_700.csv")
    # path = Path(r"D:\Downloads\2024-10-30_spiral_lamp\u_3.499_exp_16.704_4_400_1120.csv")
    path = Path(r"D:\Downloads\2024-10-30_spiral_lamp\u_3.499_exp_16.704_5_700_1120.csv")
    signals = [int(x) for x in pd.read_csv(path, skiprows=1, header=None, decimal=",")[2].to_list()]
    #[1, 2, 3, 4, 5]
    while True:
        send_signal(HOST, PORT, signals)
        sleep(5)
    