from core.utils.formater_util import format_value_by_error
import pytest


@pytest.mark.parametrize("value,error,exp_value,exp_error",
                         [
                             (2002.123,2.013,2002.0,2.0),
                             (0.3123,0.013,0.31,0.01),
                             (0.006,0.013,0.01,0.01),
                             (0.0006,0.013,0.0,0.01),
                             (10.0006,200.013,0.0,200.0),
                             (120.0006,200.013,100.0,200.0),
                         ]
                         )
def test_format_value_by_error(value:float,error:float,exp_value:float,exp_error:float)->None:
    value, error = format_value_by_error(value, error)
    assert value == exp_value
    assert error == exp_error
