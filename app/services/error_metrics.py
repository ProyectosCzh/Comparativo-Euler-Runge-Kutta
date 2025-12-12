# app/services/error_metrics.py
from typing import List, Optional, Dict
import math


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

    errors: List[float] = []
    for a, e in zip(approx, exact):
        if e != e:  # NaN
            errors.append(float("nan"))
        else:
            errors.append(abs(a - e))
    return errors


def summary_error_metrics(
    approx: List[float],
    exact: Optional[List[float]]
) -> Optional[Dict[str, Optional[float]]]:
    """
    Devuelve métricas resumen del error:
      - max: error máximo
      - rmse: raíz del error cuadrático medio

    Si exact es None, devuelve None.
    Ignora valores NaN en el cálculo.
    """
    if exact is None:
        return None

    errs = absolute_errors(approx, exact)
    if errs is None:
        return None

    # Filtramos NaN
    valid = [e for e in errs if not math.isnan(e)]
    if not valid:
        return {"max": None, "rmse": None}

    max_err = max(valid)
    rmse = math.sqrt(sum(e * e for e in valid) / len(valid))

    return {
        "max": max_err,
        "rmse": rmse
    }
