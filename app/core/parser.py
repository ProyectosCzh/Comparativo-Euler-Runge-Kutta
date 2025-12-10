# app/core/parser.py
from typing import Callable, Tuple
import sympy as sp


def parse_rhs(expr_str: str) -> Tuple[sp.Expr, Callable[[float, float], float]]:
    """
    Parsea la expresión f(t, y) dada como string usando SymPy
    y devuelve:
      - f_sym: expresión simbólica
      - f_num: función numérica f(t, y) para usar en los métodos numéricos.
    """
    t = sp.symbols('t')
    y = sp.symbols('y')

    allowed_functions = {
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "exp": sp.exp,
        "log": sp.log,
        "sqrt": sp.sqrt,
        "asin": sp.asin,
        "acos": sp.acos,
        "atan": sp.atan,
    }

    allowed_symbols = {
        "t": t,
        "y": y,
    }

    local_dict = {**allowed_symbols, **allowed_functions}

    try:
        f_sym = sp.sympify(expr_str, locals=local_dict)
    except Exception as e:
        raise ValueError(f"No se pudo interpretar la expresión f(t, y): {e}")

    # Verificación básica: que dependa de t y/o y
    if not f_sym.free_symbols.issubset({t, y}):
        raise ValueError("La expresión solo puede depender de t y y.")

    # Función numérica f(t, y)
    f_num = sp.lambdify((t, y), f_sym, modules="math")

    return f_sym, f_num
