import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from scipy.optimize import minimize
import logging

from core.calculation_module import Calculator, SpecContainer
from core.formater_util import format_error_list
logger = logging.getLogger(__name__)

class DataAdapter:
    @pytest.fixture(scope="class", autouse=True)
    def spec_container(self)->SpecContainer:
        df = pd.read_csv("tests/input_spec_2000.csv").to_numpy()
        _eps_ar = (0.3, 0.05)
        _temp = 2000.0
        container = SpecContainer(df, _temp, _eps_ar, (0, 1))
        # container.calib_signal = np.ones(container.calib_signal.shape)
        # container.set_spec(df[:, 1])
        container.set_spec(df[:, 1]/container.eps_val(_eps_ar)/container.lbb(_temp)*df[:, 1])
        return container
    

class TestResult(DataAdapter):
    def test_calculation_result(self, spec_container: SpecContainer) -> None:
        calculator = Calculator(spec_container)
        expected = json.loads(Path("tests/result_data.json").read_text(encoding="utf-8"))
        exp_ans_arr: list[float] = [expected["temp"]]+expected["eps"]
        exp_cov: list[float] = expected["cov"]
        exp_ans_arr, exp_cov = format_error_list(exp_ans_arr, exp_cov) 
        # logger.debug("wl: %s", spec_container.wave_lengths)
        # logger.debug("i: %s", spec_container.signals)
        t_vin = spec_container.estimate_vin()
        t_0 = float(minimize(calculator.s2, t_vin, method="Nelder-Mead").x[0])
        eps = calculator.eps_arr(t_0)
        ans_arr = [t_0]+list(eps)
        cov: list[float] = list(calculator.cov_matrix(t_0))
        ans_arr, cov = format_error_list(ans_arr, cov)
        for idx, val in enumerate(exp_ans_arr):
            logger.debug("ans: %s +/- %s", ans_arr[idx], cov[idx])
            logger.debug("expected: %s +/- %s", val, exp_cov[idx])
            assert ans_arr[idx] == val
            assert cov[idx] == exp_cov[idx]
        