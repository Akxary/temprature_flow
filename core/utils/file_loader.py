from pathlib import Path
from threading import Lock
from tkinter import filedialog

import numpy as np
import numpy.typing as npt
from core.calculation_module import SpecContainer
from core.config import Config
from core.interfaces import (
    GetModelProtocol,
    LoggerProtocol,
    ServerThreadProtocol,
    SpecContainerProtocol,
    ServerProtocol,
)
import pandas as pd


class FileLoaderMixin(
    LoggerProtocol,
    GetModelProtocol,
    SpecContainerProtocol,
    ServerProtocol,
    ServerThreadProtocol,
):
    def __start_server(self) -> None:
        try:
            if not self.server_thread.is_alive():
                self.start_server()
        except Exception as e:
            self.logger.error("Error starting server: %s", e)

    def load_bkg(self) -> None:
        csv_data = self.load_file()
        if csv_data is None:
            return
        try:
            with Lock():
                self.container.set_bkg(csv_data)
            self.logger.info("Background file loaded")
        except Exception as e:
            self.logger.error("Error initializating bkg file: %s", e)
            return
    
    def load_calibr(self) -> None:
        csv_data = self.load_file()
        if csv_data is None:
            return
        try:
            eps_model, eps_tuple = self.get_model()
            with Lock():
                self.container = SpecContainer(
                    csv_data,
                    self.temp_var.get(),
                    eps_tuple,
                    eps_model,
                )
            self.logger.info("Calibration file loaded")
        except Exception as e:
            self.logger.error("Error initializating calibraion file: %s", e)
            return
        self.__start_server()
        
    def load_file(self) -> npt.NDArray[np.float64] | None:
        """Обработчик загрузки файла."""
        file_path_str = filedialog.askopenfilename()
        if not file_path_str:
            self.logger.error(
                "No file selected:"
            )
            return None
        file_path = Path(file_path_str)
        self.logger.info("Got file path: %s", file_path)
        if not file_path.is_file() or file_path.suffix != ".csv":
            self.logger.error(
                "Unexpected file format: %s. Expected '.csv'", file_path.suffix
            )
            return None
        try:
            csv_data = pd.read_csv(file_path, skiprows=1, header=None, decimal=",")[list(Config.CALIB_WL_I)].to_numpy()
            csv_data[:, 1] = csv_data[:, 1].astype(np.float64)/self.exp_var.get()
            csv_data[:, 1] = np.where(csv_data[:, 1]<=0, np.ones(csv_data[:, 1].shape), csv_data[:, 1])
            return csv_data
        except Exception as e:
            self.logger.error("Unexpected file format produced error: %s", e)
            return None
