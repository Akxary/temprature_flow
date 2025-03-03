from datetime import datetime
from core.interfaces import FileWriteCheckProtocol, LoggerProtocol
import numpy.typing as npt
import numpy as np
import pandas as pd
from core.config import base_path


class FileWriterMixin(LoggerProtocol):
    # def __init__(self) -> None:
    #     self._tgt_dir = base_path / "specs"
    #     self._tgt_dir.mkdir(exist_ok=True)
    #     self.logger.info("Target spec dir created at: %s", self._tgt_dir)

    def write(
        self,
        cur_time: datetime,
        wave_length: npt.NDArray[np.float64],
        raw_signal: npt.NDArray[np.float64],
        corrected_signal: npt.NDArray[np.float64],
    ) -> None:
        self._tgt_dir = base_path / "specs"
        self._tgt_dir.mkdir(exist_ok=True)
        str_date = cur_time.strftime("%Y-%m-%d")
        date_dir = self._tgt_dir / str_date
        date_dir.mkdir(exist_ok=True)
        file_name = cur_time.strftime("%H_%M_%S_%f") + ".csv"
        file_path = date_dir / file_name
        self.logger.info("Writting spec to %s", file_path)
        pd.DataFrame(
            np.concatenate(
                [
                    wave_length[:, np.newaxis],
                    raw_signal[:, np.newaxis],
                    corrected_signal[:, np.newaxis],
                ],
                axis=1,
            ),
            columns=[
                "wl (длина волны), мкм",
                "I (исходный сигнал)",
                "I (скорректированный сигнал)",
            ],
        ).to_csv(file_path, index=False)
