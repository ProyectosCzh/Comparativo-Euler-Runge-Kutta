from typing import Callable
import math
import sympy as sp

from app.schemas.ode_schemas import EquationInput, InitialCondition


def get_predefined_f_and_analytic(
    eq: EquationInput, ic: InitialCondition
) -> tuple[Callable, Callable, str]:
    """
    Catálogo mínimo:
    - exp_growth: y' = λ y, solución analítica cerrada.
    """
    if eq.id == "exp_growth":
        lam = eq.params.get("lambda", -1.0)
        x0 = ic.x0
        y0 = ic.y0

        def f(x, y):
            return lam * y

        def analytic(x):
            return y0 * math.exp(lam * (x - x0))

        expression_str = f"{y0}*exp({lam}*(x-{x0}))"
        return f, analytic, expression_str

    raise ValueError(f"Ecuación predefinida no soportada: {eq.id}")


def build_custom_f(eq: EquationInput):
    """
    Construye f(x,y) a partir de una expresión string usando SymPy.
    Sin solución analítica.
    """
    if not eq.expression:
        raise ValueError("Para ecuaciones custom debes enviar 'expression'")

    vars_list = eq.variables or ["x", "y"]
    if len(vars_list) != 2:
        raise ValueError("Solo se soportan ecuaciones en dos variables: x, y")

    x_name, y_name = vars_list
    x_sym, y_sym = sp.symbols(f"{x_name} {y_name}", real=True)
    expr = sp.sympify(eq.expression)

    f_py = sp.lambdify((x_sym, y_sym), expr, modules="math")

    def f(x, y):
        return float(f_py(x, y))

    return f
