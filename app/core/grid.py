# app/core/grid.py
from typing import List


def build_time_grid(t0: float, T: float, h: float, max_points: int = 5000) -> List[float]:
    if h <= 0:
        raise ValueError("El paso h debe ser positivo.")
    if T <= t0:
        raise ValueError("Se requiere T > t0 para construir el intervalo.")

    n_estimated = int((T - t0) / h) + 2  # +2 por seguridad
    if n_estimated > max_points:
        raise ValueError(
            f"El número de puntos estimado ({n_estimated}) excede el máximo permitido ({max_points}). "
            f"Reduce el intervalo o aumenta h."
        )

    grid = []
    t = t0
    # Usamos una pequeña tolerancia para incluir T
    T_tol = T + 1e-12
    while t < T_tol:
        grid.append(t)
        t += h

    # Ajustar el último valor al T exacto si quedó muy cerca
    if abs(grid[-1] - T) > 1e-8:
        grid.append(T)

    return grid
