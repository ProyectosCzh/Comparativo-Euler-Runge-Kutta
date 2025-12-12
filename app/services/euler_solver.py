# app/services/euler_solver.py
from typing import List, Callable, Tuple
from app.core.grid import build_time_grid



def euler_solver(
    f_num: Callable[[float, float], float],
    t0: float,
    y0: float,
    T: float,
    h: float
) -> Tuple[List[float], List[float]]:
    """
    Resuelve y' = f(t, y) con método de Euler explícito.
    Devuelve:
      - grid de tiempo
      - lista de y_n
    """
    grid = build_time_grid(t0, T, h)
    y_values: List[float] = [y0]

    for i in range(len(grid) - 1):
        t_n = grid[i]
        y_n = y_values[-1]
        h_n = grid[i+1] - grid[i]  # por si el último paso se ajusta a T

        k1 = f_num(t_n, y_n)
        y_next = y_n + h_n * k1
        y_values.append(float(y_next))

    return grid, y_values
