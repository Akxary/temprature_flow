from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
from pathlib import Path
from threading import Event, Lock, Thread
import customtkinter as ctk # type: ignore
from tkinter import filedialog
from cycler import V
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk # type: ignore
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import numpy as np

from core.calculation_module import SpecContainer
from core.utils.file_loader import FileLoaderMixin
from core.utils.file_writer import FileWriterMixin
from core.utils.get_model_util import GetModelMixin
from core.utils.logger import SetupLoggerMixin
from core.utils.set_model import SetModelMixin
from core.utils.start_server import StartServerMixin

# Настройка внешнего вида
ctk.set_appearance_mode("Dark")  # Режим оформления: System, Dark, Light
ctk.set_default_color_theme("blue")  # Цветовая тема


class App(
    ctk.CTk, # type: ignore
    SetupLoggerMixin,
    FileLoaderMixin,
    FileWriterMixin,
    StartServerMixin,
    GetModelMixin,
    SetModelMixin,
):
    def __init__(self) -> None:
        super().__init__()
        # background thread
        self.server_thread: Thread = Thread(daemon=True)
        # воркеры для записи файлов
        self.thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=3)
        # result array
        self.time_arr: list[datetime] = []
        self.temp_arr: list[float] = []  # [2000.0]
        self.temp_err_arr: list[float] = []  # [2.0]
        # variables
        self.exp_var = ctk.DoubleVar(value=16.23)
        self.temp_var = ctk.DoubleVar(value=2200.0)
        self.e0_var = ctk.DoubleVar(value=0.5)
        self.e1_var = ctk.DoubleVar(value=0.0)
        self.e1_check_var = ctk.BooleanVar(value=False)
        self.e2_var = ctk.DoubleVar(value=0.0)
        self.e2_check_var = ctk.BooleanVar(value=False)
        self.res_var = ctk.StringVar(value="-")
        self.file_write_check_var= ctk.BooleanVar(value=True)
        
        
        self.title("Temperature measumrement flow")
        # self.geometry("950x550")
        self.container: SpecContainer
        self.left_frame = ctk.CTkFrame(self)
        self.right_frame = ctk.CTkFrame(self)
        self.grid_rowconfigure(0, weight=1)  # Вес для строки
        self.grid_columnconfigure(0, weight=1)  # Вес для первого столбца
        self.grid_columnconfigure(1, weight=1)  # Вес для второго столбца
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        for i in range(3):
            self.left_frame.grid_rowconfigure(i, weight=1)
        for i in range(10):
            self.left_frame.grid_columnconfigure(i, weight=1)

        self.text_box = ctk.CTkTextbox(self.left_frame, width=600, height=350)
        self.logger = logging.getLogger("AppLogger")
        self.setup_logger()

        # 1. Поля с CheckBox, связанные с переменными
        exposure_label = ctk.CTkLabel(self.left_frame, text="exp(ms)=")
        exposure_entry = ctk.CTkEntry(self.left_frame, textvariable=self.exp_var)
        temp_label = ctk.CTkLabel(self.left_frame, text="T(K)=")
        temp_entry = ctk.CTkEntry(self.left_frame, textvariable=self.temp_var)
        e0_label = ctk.CTkLabel(self.left_frame, text="e0=")
        e0_entry = ctk.CTkEntry(self.left_frame, textvariable=self.e0_var)
        e1_label = ctk.CTkLabel(self.left_frame, text="e1(1/µm)=")
        e1_entry = ctk.CTkEntry(
            self.left_frame,
            textvariable=self.e1_var,
            state="disabled",
        )
        e1_ckbx = ctk.CTkCheckBox(
            self.left_frame,
            text="",
            width=24,
            variable=self.e1_check_var,
            command=lambda: self.update_check_box(self.e1_check_var, e1_entry),
        )
        e2_label = ctk.CTkLabel(self.left_frame, text="e2(1/µm2)=")
        e2_entry = ctk.CTkEntry(
            self.left_frame,
            textvariable=self.e2_var,
            state="disabled",
        )
        e2_ckbx = ctk.CTkCheckBox(
            self.left_frame,
            text="",
            width=24,
            variable=self.e2_check_var,
            command=lambda: self.update_check_box(self.e2_check_var, e2_entry),
        )
        file_write_ckbk = ctk.CTkCheckBox(
            self.left_frame,
            text="Включить запись в файл",
            variable=self.file_write_check_var,
        )

        # 2. Кнопка для загрузки файла калибровки
        load_calibr_button = ctk.CTkButton(
            self.left_frame,
            text="Загрузить калибровочный файл",
            command=self.load_calibr,
        )
        # Кнопка для загрузки файла бэкграунда
        load_bckg_button = ctk.CTkButton(
            self.left_frame,
            text="Загрузить файл с фоном",
            command=self.load_bkg,
        )
        # Кнопка установки модели
        set_model_button = ctk.CTkButton(
            self.left_frame,
            text="Установить модель",
            command=self.set_model,
        )
        # Кнопка очистки графика температур
        clear_temp_button = ctk.CTkButton(
            self.left_frame,
            text="Очистить график температур",
            command=self.clear_temp_plot,
        )
        
        # 4. Результирующий вывод
        res_temp_label = ctk.CTkLabel(self.left_frame, text="Вычисленная температура:")
        res_temp_entry = ctk.CTkEntry(self.left_frame, textvariable=self.res_var, state="disabled")
        
        # Расположение виджетов
        clear_temp_button.grid(row=0, column=0, columnspan=3, pady=5, padx=5)
        exposure_label.grid(row=1, column=1, pady=5, padx=5)
        exposure_entry.grid(row=1, column=2, pady=5, padx=5)
        temp_label.grid(row=2, column=1, pady=5, padx=5)
        temp_entry.grid(row=2, column=2, pady=5, padx=5)
        e0_label.grid(row=3, column=1, pady=5, padx=5)
        e0_entry.grid(row=3, column=2, pady=5, padx=5)
        e1_ckbx.grid(row=4, column=0, pady=5, padx=5)
        e1_label.grid(row=4, column=1, pady=5, padx=5)
        e1_entry.grid(row=4, column=2, pady=5, padx=5)
        e2_ckbx.grid(row=5, column=0, pady=5, padx=5)
        e2_label.grid(row=5, column=1, pady=5, padx=5)
        e2_entry.grid(row=5, column=2, pady=5, padx=5)
        set_model_button.grid(row=6, columnspan=3, column=0, pady=5, padx=5)
        load_calibr_button.grid(row=7, columnspan=2, column=0, pady=5, padx=5)
        load_bckg_button.grid(row=7, columnspan=1, column=2, pady=5, padx=5)
        file_write_ckbk.grid(row=8, columnspan=3, column=0, pady=5, padx=5)
        res_temp_label.grid(row=9, columnspan=3, column=0, pady=5, padx=5)
        res_temp_entry.grid(row=10, columnspan=3, column=0, pady=5, padx=5)
        # Инициализация графиков
        # 6. Прокручиваемый текстовый бокс для логов
        self.text_box.grid(row=11, column=0, sticky="nsew", pady=10, padx=5, columnspan=3)

        # 5. График текущей температуры
        self.fig_frame = ctk.CTkFrame(self.right_frame, width=650, height=400)
        self.fig_frame.pack(expand=True)
        # Добавляем панель инструментов для масштабирования и панорамирования
        self.figure = Figure(figsize=(7, 5), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.fig_frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.fig_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(pady=10, padx=5)
        # График текущего спектра
        self.spec_fig_frame = ctk.CTkFrame(self.right_frame, width=650, height=400)
        # self.spec_fig_frame.grid(row=9, columnspan=3, column=0, pady=10, padx=5)
        self.spec_fig_frame.pack(expand=True)
        self.spec_figure = Figure(figsize=(7, 5), dpi=100)
        self.spec_plot = self.spec_figure.add_subplot(111)
        self.spec_canvas = FigureCanvasTkAgg(self.spec_figure, master=self.spec_fig_frame)
        self.spec_toolbar = NavigationToolbar2Tk(self.spec_canvas, self.spec_fig_frame)
        self.spec_toolbar.update()
        self.spec_canvas.get_tk_widget().pack(pady=10, padx=5)
        

    def update_check_box(self, var: ctk.BooleanVar, entry: ctk.CTkEntry) -> None:
        if var.get():
            entry.configure(state="normal")
        else:
            entry.configure(state="disabled")

    def clear_temp_plot(self) -> None:
        with Lock():
            self.time_arr = []
            self.temp_arr = []
            self.temp_err_arr = []
        self._update_temp_plot()
    
    def _update_temp_plot(self) -> None:
        self.logger.info("Updating temperature plot")
        self.plot.clear()
        self.plot.errorbar(np.array(self.time_arr), self.temp_arr, self.temp_err_arr, marker="o")
        self.plot.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        self.plot.set_xlabel("Текущее время")
        self.plot.set_ylabel("Температура, К")
        self.canvas.draw()
        
    def _update_spec_plot(self, eps_arr: tuple[float, ...]) -> None:
        self.logger.info("Updating spec plot")
        self.spec_plot.clear()
        self.spec_plot.plot(self.container.wave_lengths, self.container.signals, linewidth=0, marker="p", markersize=3, label="signal")
        self.spec_plot.plot(self.container.wave_lengths, self.container.eps_val(eps_arr)*self.container.lbb(self.temp_var.get()), linewidth=3, linestyle="--", label="model")
        self.spec_plot.ticklabel_format(axis="y", useMathText=True)
        self.spec_plot.set_xlabel(r"$\lambda,\ \mu m$", loc="right", labelpad=-35)
        self.spec_plot.set_ylabel("I", loc="top", rotation=0, labelpad=-5)
        self.spec_plot.legend()
        self.spec_canvas.draw()
        
    def update_plot(self, eps_arr: tuple[float, ...]) -> None:
        self._update_temp_plot()
        self._update_spec_plot(eps_arr)
        