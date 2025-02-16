from pathlib import Path
from tkinter import filedialog

import numpy as np
from core.calculation_module import SpecContainer
from core.interfaces import (
    GetModelProtocol,
    LoggerProtocol,
    SpecContainerProtocol,
    ServerProtocol,
    StopEventProtocol,
)
import pandas as pd


class FileLoaderMixin(
    LoggerProtocol,
    GetModelProtocol,
    SpecContainerProtocol,
    ServerProtocol,
    StopEventProtocol,
):
    def load_file(self) -> None:
        """Обработчик загрузки файла."""
        file_path_str = filedialog.askopenfilename()
        if not file_path_str:
            return
        file_path = Path(file_path_str)
        self.logger.info("Got file path: %s", file_path)
        if not file_path.is_file() or file_path.suffix != ".csv":
            self.logger.error(
                "Unexpected file format: %s. Expected '.csv'", file_path.suffix
            )
            return
        try:
            csv_data = pd.read_csv(file_path, skiprows=1, header=None, decimal=",")[[4, 5]].to_numpy()
            csv_data[:, 1] = csv_data[:, 1].astype(np.float64)/self.exp_var.get()
            csv_data[:, 1] = np.where(csv_data[:, 1]<=0, np.ones(csv_data[:, 1].shape), csv_data[:, 1])
        except Exception as e:
            self.logger.error("Unexpected file format produced error: %s", e)
            return
        try:
            eps_model, eps_tuple = self.get_model()
            self.container = SpecContainer(
                csv_data,
                self.temp_var.get(),
                eps_tuple,
                eps_model,
            )
        except Exception as e:
            self.logger.error("Error initializating calibraion file: %s", e)
            return
        try:
            if self.server_thread.is_alive():
                self.stop_event.set()
                self.server_thread.join()
            self.logger.info("Starting server...")
            self.start_server()
        except Exception as e:
            self.logger.error("Error starting server: %s", e)
        # self.spec_container = SpecContainer()
