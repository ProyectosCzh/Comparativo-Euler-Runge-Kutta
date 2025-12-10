# app/services/rk4_solver.py
from typing import List, Callable
from core.grid import build_time_grid


def rk4_solver(
    f_num: Callable[[float, float], float],
    t0: float,
    y0: float,
    T: float,
    h: float
) -> (List[float], List[float]):
    """
    Resuelve y' = f(t, y) con el método clásico de Runge-Kutta de orden 4 (RK4).
    Devuelve:
      - grid de tiempo
      - lista de y_n
    """
    grid = build_time_grid(t0, T, h)
    y_values: List[float] = [y0]

    for i in range(len(grid) - 1):
        t_n = grid[i]
        y_n = y_values[-1]
        h_n = grid[i+1] - grid[i]  # ajustar último paso

        k1 = f_num(t_n, y_n)
        k2 = f_num(t_n + 0.5 * h_n, y_n + 0.5 * h_n * k1)
        k3 = f_num(t_n + 0.5 * h_n, y_n + 0.5 * h_n * k2)
        k4 = f_num(t_n + h_n, y_n + h_n * k3)

        y_next = y_n + (h_n / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        y_values.append(float(y_next))

    return grid, y_values
