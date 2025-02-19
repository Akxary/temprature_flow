from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM, timeout
from threading import Lock, Thread

import numpy as np

from core.calculation_module import calculate_temp_with_errors
from core.interfaces import (
    LoggerProtocol,
    ResContainerProtocol,
    SpecContainerProtocol,
    StopEventProtocol,
    UpdatePlotProtocol,
)
from core.socket_adapter import recieve_signal
from core.config import Config


class StartServerMixin(
    LoggerProtocol,
    SpecContainerProtocol,
    StopEventProtocol,
    ResContainerProtocol,
    UpdatePlotProtocol,
):
    def start_server(self) -> None:
        self.server_thread = Thread(
            target=self._start_server,
            args=(
                Config.HOST,
                Config.PORT,
            ),
            daemon=True,
        )
        self.server_thread.start()

    def _start_server(self, host: str, port: int) -> None:
        # Создание серверного сокета
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((host, port))
        # Максимальное количество ожидающих соединений
        server_socket.listen(5)
        self.logger.info("Server listening %s:%s", host, port)

        while True:
            try:
                server_socket.settimeout(1.0)
                # Принятие соединения от клиента
                client_socket, client_address = server_socket.accept()
                self.logger.info(
                    f"Client connected: %s:%s",
                    client_address,
                    client_socket,
                )

                try:
                    # Обработка данных от клиента
                    signals = np.array(recieve_signal(client_socket)).astype(np.float64)/self.exp_var.get()
                    self.logger.info(
                        f"Recieved signals <%s>: %s...",
                        signals.shape[0],
                        signals[:5],
                    )
                    # Вычисление температуры
                    signals = np.where(signals <= 0, np.ones(signals.shape), signals)
                    with Lock():
                        self.container.set_spec(signals)
                        res, res_err = calculate_temp_with_errors(self.container)
                    self.time_arr.append(datetime.now())
                    self.temp_arr.append(res[0])
                    self.temp_err_arr.append(res_err[0])
                    # обновление результирующей переменной
                    self.res_var.set(f"{res[0]} ± {res_err[0]} (K)")
                    # отрисовка нового графика
                    self.update_plot()

                except Exception as e:
                    self.logger.error("Error recieving data: %s", e)
                finally:
                    # Закрытие соединения с клиентом
                    client_socket.close()
                    self.logger.info(
                        "Connection with %s:%s closed",
                        client_address,
                        client_socket,
                    )
            except timeout:
                continue
            except Exception as e:
                self.logger.error("Server error: %s", e)
                break

        server_socket.close()
        self.logger.info("Server stopped")
