# app/services/error_metrics.py
from typing import List, Optional, Dict


def absolute_errors(
    approx: List[float],
    exact: Optional[List[float]]
) -> Optional[List[float]]:
    """
    Calcula errores absolutos |approx - exact| punto a punto.
    Si exact es None, devuelve None.
    """
    if exact is None:
        return None

    if len(approx) != len(exact):
        raise ValueError("Las listas approx y exact deben tener la misma longitud.")

    errors = []
    for a, e in zip(approx, exact):
        if e != e:  # NaN
            errors.append(float("nan"))
        else:
            errors.append(abs(a - e))
    return errors
