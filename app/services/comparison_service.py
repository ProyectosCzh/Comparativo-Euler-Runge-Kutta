from typing import List
import math

from app.schemas.ode_schemas import SimpleError


def compute_pointwise_errors(y_num: List[float], y_ref: List[float]) -> SimpleError:
    if len(y_num) != len(y_ref):
        raise ValueError("Las longitudes de y_num y y_ref deben coincidir")

    n = len(y_num)
    if n == 0:
        return SimpleError(max=0.0, rmse=0.0)

    errors = [abs(a - b) for a, b in zip(y_num, y_ref)]
    max_err = max(errors)
    mse = sum(e ** 2 for e in errors) / n
    rmse = math.sqrt(mse)
    return SimpleError(max=max_err, rmse=rmse)
