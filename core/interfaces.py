from concurrent.futures import ThreadPoolExecutor
import logging
from threading import Event, Thread
from typing import Protocol

from customtkinter import CTkTextbox, BooleanVar, DoubleVar, StringVar # type: ignore

from core.calculation_module import SpecContainer


class LoggerProtocol(Protocol):
    logger: logging.Logger


class TextBoxProtocol(Protocol):
    text_box: CTkTextbox


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
    def get_model(self)->tuple[tuple[int,...], tuple[float,...]]:...

class UpdatePlotProtocol(Protocol):
    def update_plot(self)->None:...


class ServerProtocol(Protocol):
    def start_server(self)->None:...
    
class ThreadPoolProtocol(Protocol):
    thread_pool: ThreadPoolExecutor

class StopEventProtocol(Protocol):
    server_thread: Thread
    stop_event: Event

class ResContainerProtocol(Protocol):
    time_arr: list[str]
    temp_arr: list[float]
    temp_err_arr: list[float] 
    res_var: StringVar
    