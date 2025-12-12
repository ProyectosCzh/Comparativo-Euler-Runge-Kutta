# app/services/analytic_solver.py
from typing import List, Optional, Tuple
import sympy as sp
from app.core.grid import build_time_grid


def analytic_solver(
    f_sym: sp.Expr,
    t0: float,
    y0: float,
    T: float,
    h: float
) -> Tuple[List[float], Optional[List[float]], dict]:

    """
    Intenta resolver analíticamente la EDO:
        y'(t) = f_sym(t, y(t))
    con condición inicial y(t0) = y0.

    Devuelve:
      - grid de tiempo
      - exact_values: lista de y_exact(t_n) o None si no se pudo resolver
      - meta: dict con info simbólica (ecuación, latex, estado)
    """

    t = sp.symbols('t')
    y = sp.Function('y')
    # Sustituir el símbolo y por y(t) en f_sym si es necesario
    f_sym_subs = f_sym
    y_sym = sp.symbols('y')
    if f_sym.has(y_sym):
        f_sym_subs = f_sym.subs(y_sym, y(t))

    ode = sp.Eq(sp.diff(y(t), t), f_sym_subs)
    grid = build_time_grid(t0, T, h)

    meta = {
        "ode_simplified": str(ode),
        "exact_solution_latex": None,
        "analytic_status": None
    }

    try:
        sol = sp.dsolve(ode, ics={y(t0): y0})
    except Exception:
        meta["analytic_status"] = "failed"
        return grid, None, meta

    # Si dsolve no lanza error pero devuelve algo raro, lo manejamos
    try:
        y_exact_expr = sol.rhs  # y(t) = RHS
    except Exception:
        meta["analytic_status"] = "failed"
        return grid, None, meta

    meta["analytic_status"] = "ok"
    meta["exact_solution_latex"] = sp.latex(sp.Eq(y(t), y_exact_expr))

    # Construimos función numérica y_exact(t)
    y_exact_num = sp.lambdify(t, y_exact_expr, modules="math")

    exact_values: List[float] = []
    for ti in grid:
        try:
            val = float(y_exact_num(ti))
            # Verificar que el valor sea finito (no inf, -inf, nan)
            if not (val == val and abs(val) != float('inf')):  # Chequeo de NaN e Inf
                val = None
        except Exception:
            val = None
        exact_values.append(val)

    return grid, exact_values, meta
