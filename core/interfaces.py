from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
from threading import Thread
from typing import Protocol
import numpy as np
import numpy.typing as npt

from customtkinter import CTkTextbox, BooleanVar, DoubleVar, StringVar  # type: ignore

from core.calculation_module import SpecContainer


class LoggerProtocol(Protocol):
    logger: logging.Logger


class TextBoxProtocol(Protocol):
    text_box: CTkTextbox


class FileWriteCheckProtocol(Protocol):
    file_write_check_var: BooleanVar


class FileWriterProtocol(Protocol):
    def write(
        self,
        cur_time: datetime,
        wave_length: npt.NDArray[np.float64],
        raw_signal: npt.NDArray[np.float64],
        corrected_signal: npt.NDArray[np.float64],
    ) -> None: ...


class SpecContainerProtocol(Protocol):
    container: SpecContainer
    exp_var: DoubleVar
    temp_var: DoubleVar
    e0_var: DoubleVar
    e1_check_var: BooleanVar
    e1_var: DoubleVar
    e2_check_var: BooleanVar
    e2_var: DoubleVar


class GetModelProtocol(SpecContainerProtocol, Protocol):
    def get_model(self) -> tuple[tuple[int, ...], tuple[float, ...]]: ...


class UpdatePlotProtocol(Protocol):
    def update_plot(self, eps_arr: tuple[float, ...]) -> None: ...


class ServerProtocol(Protocol):
    def start_server(self) -> None: ...


class ThreadPoolProtocol(Protocol):
    thread_pool: ThreadPoolExecutor

class ServerThreadProtocol(Protocol):
    server_thread: Thread

class ResContainerProtocol(Protocol):
    time_arr: list[datetime]
    temp_arr: list[float]
    temp_err_arr: list[float]
    res_var: StringVar
