from typing import MutableSequence, TypeVar
from math import log10

MS = TypeVar("MS",  bound=MutableSequence[float])

def format_value_by_error(value: float, error: float) -> tuple[float, float]:
    if error == 0.0:
        return round(value, 0), error
    er_pow = int(log10(abs(error)))
    if er_pow < 0:
        er_pow -= 1
    return round(value, -er_pow), round(error, -er_pow)

def format_error_list(value_list: MS, error_list: MS) -> tuple[MS, MS]:
    for idx, val in enumerate(value_list):
        _val, _err = format_value_by_error(val, error_list[idx])
        value_list[idx] = _val
        error_list[idx] = _err
    return value_list, error_list