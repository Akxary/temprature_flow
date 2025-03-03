from typing import Literal, cast
import numpy.typing as npt
from scipy.optimize import minimize
from scipy.stats import t
import numpy as np
import math
from math import pow

from core.utils.formater_util import format_error_list


c_1 = 2 * math.pi * 6.62607015 * pow(2.99792458, 2) * pow(10, 12)
c_2 = 6.62607015 * 2.99792458 / 1.38 * pow(10, 3)


class SpecContainer:
    bkg = np.zeros((1,))
    def __init__(
        self,
        calib_spec: npt.NDArray[np.float64],
        calib_temp: float,
        calib_eps: tuple[float, ...],
        model: tuple[int, ...] = (0,),
    ) -> None:
        if calib_spec.ndim != 2:
            raise ValueError("Calib array should be 2 dimensional")
        self.wave_lengths = calib_spec[:, 0]
        # if nanometers is passed
        if self.wave_lengths.mean() // 100 > 1:
            self.wave_lengths /= 1000
        self.model = model
        self._base_spec = calib_spec[:, 1].astype(np.float64)
        self.calib_signal = (
            self._base_spec / self.lbb(calib_temp) / self.eps_val(calib_eps)
        )
        self.signals = np.ones(self.calib_signal.shape)
        if self.bkg.shape[0] != self.signals.shape[0]:
            self.set_bkg(np.zeros((self.signals.shape[0],2)))

    def eps_val(
        self,
        eps_ar: tuple[float, ...] | npt.NDArray[np.float64],
    ) -> npt.NDArray[np.float64]:
        return cast(
            npt.NDArray[np.float64],
            sum(
                np.power(self.wave_lengths, idx) * val
                for idx, val in zip(self.model, eps_ar)
            ),
        )

    def lbb(self, temp: float) -> npt.NDArray[np.float64]:
        return cast(
            npt.NDArray[np.float64],
            c_1
            / np.power(self.wave_lengths, 5)
            / (np.exp(c_2 / temp / self.wave_lengths) - 1),
        )

    def set_spec(self, signals: npt.NDArray[np.float64]) -> None:
        if signals.ndim != 1 or signals.shape[0] != self.wave_lengths.shape[0]:
            raise ValueError("Incorrect input signal")
        self.signals = (signals.astype(np.float64) - self.bkg) / self.calib_signal
    
    def set_bkg(self, bkg: npt.NDArray[np.float64]) -> None:
        if bkg.ndim != 2 or bkg.shape[0] != self.wave_lengths.shape[0]:
            raise ValueError("Incorrect input background")
        self.bkg = bkg[:, 1].astype(np.float64)

    def set_model(
        self,
        calib_temp: float,
        new_model: tuple[int, ...],
        eps_ar: tuple[float, ...] | npt.NDArray[np.float64],
    ) -> None:
        self.model = new_model
        self.signals *= self.calib_signal
        self.calib_signal = (
            self._base_spec / self.lbb(calib_temp) / self.eps_val(eps_ar)
        )
        self.signals /= self.calib_signal

    


class Calculator:
    def __init__(
        self,
        container: SpecContainer,
        weights: Literal["N", "I"] = "N",
    ):
        self.container = container
        self.model: tuple[int, ...] = container.model
        self.weights = weights
        self.w = np.ones(self.container.signals.shape)
        if weights == "I":
            self.w = cast(npt.NDArray[np.float64], np.power(
                np.where(
                    self.container.signals == 0,
                    np.zeros(self.container.signals.shape),
                    1 / self.container.signals,
                ),
                2,
            ))
        self.w_mat = np.diagflat(self.w)

    def estimate_vin(self) -> float:
        y = np.log(self.container.signals * np.power(self.container.wave_lengths, 5) / c_1)
        x = c_2 / self.container.wave_lengths
        a, _ = np.polyfit(x, y, deg=1)
        return float(-1 / a)
    
    def j_matrix_t(self, temp: float) -> npt.NDArray[np.float64]:
        """To find eps_arr, not for covariance matrix"""
        return np.array(
            [
                self.container.lbb(temp) * np.power(self.container.wave_lengths, j)
                for j in self.model
            ]
        ).transpose()

    def eps_arr(self, temp: float) -> npt.NDArray[np.float64]:
        """Solution for emissivity"""
        j_mat = self.j_matrix_t(temp)
        j_mat_t = j_mat.transpose()
        sign_vec = self.container.signals[:, np.newaxis]
        sign_vec = self.w_mat.dot(sign_vec)
        j_mat_t_x_j_mat_r = np.linalg.inv(j_mat_t.dot(self.w_mat).dot(j_mat))
        return cast(
            npt.NDArray[np.float64],
            j_mat_t_x_j_mat_r.dot(j_mat_t).dot(sign_vec).reshape(len(self.model)),
        )

    def j_matrix(self, temp: float) -> npt.NDArray[np.float64]:
        """For covariance matrix creation"""
        ar = self.eps_arr(temp)
        j_mat_0 = [
            (
                self.container.eps_val(ar)
                * np.power(self.container.lbb(temp), 2)
                * np.power(self.container.wave_lengths, 4)
                * c_2
                / c_1
                / pow(temp, 2)
                * np.exp(c_2 / self.container.wave_lengths / temp)
            )[:, np.newaxis]
        ]
        j_mat_1 = [
            (self.container.lbb(temp) * np.power(self.container.wave_lengths, j))[
                :, np.newaxis
            ]
            for j in self.model
        ]
        return cast(
            npt.NDArray[np.float64],
            np.concatenate(j_mat_0 + j_mat_1, axis=1),
        )

    def cov_matrix(self, temp: float) -> npt.NDArray[np.float64]:
        """Array of errors"""
        # classic solution
        n, m = len(self.container.wave_lengths), len(self.model)
        sigma = self.s2(temp) / (n - m - 1)
        j_mat = self.j_matrix(temp)
        j_mat_t_x_j_mat = j_mat.transpose().dot(self.w_mat).dot(j_mat)
        errors = np.sqrt(
            np.diagonal(np.linalg.inv(j_mat_t_x_j_mat))
            * sigma
            * t.interval(0.95, n - m - 1)[1]
        )
        return cast(npt.NDArray[np.float64], errors.reshape((errors.shape[0])))

    def s2(self, temp: float) -> float:
        arr = self.eps_arr(temp)
        return float(sum(
            self.w
            * np.power(
                self.container.signals
                - self.container.eps_val(arr) * self.container.lbb(temp),
                2,
            )
        ))


def calculate_temp_with_errors(spec_container: SpecContainer)->tuple[list[float], list[float]]:
    calculator = Calculator(spec_container)
    t_vin = calculator.estimate_vin()
    t_0 = float(minimize(calculator.s2, t_vin, method="Nelder-Mead").x[0]) # type: ignore
    eps = calculator.eps_arr(t_0)
    ans_arr = [t_0]+list(eps)
    cov: list[float] = list(calculator.cov_matrix(t_0))
    ans_arr, cov = format_error_list(ans_arr, cov)
    return ans_arr, cov
