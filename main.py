from typing import List, Literal, Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import math
import time
import sympy as sp

# ============================================================
# 1. MODELOS DE ENTRADA / SALIDA (SCHEMAS)
# ============================================================

class EquationInput(BaseModel):
    """
    Representa la EDO en la entrada.
    Backend solo interpreta la ecuación; nada de texto pedagógico.
    """
    type: Literal["predefined", "custom"]
    id: Optional[Literal["exp_growth"]] = None  # catálogo predefinido mínimo
    params: Dict[str, float] = Field(default_factory=dict)

    # Custom
    expression: Optional[str] = None  # ej: "x*y - 2*x"
    variables: Optional[List[str]] = None  # normalmente ["x", "y"]


class InitialCondition(BaseModel):
    x0: float
    y0: float


class Domain(BaseModel):
    x_end: float


class SolveRequest(BaseModel):
    equation: EquationInput
    initial_condition: InitialCondition
    domain: Domain
    step: float = Field(gt=0, description="Tamaño de paso h > 0")
    methods: List[Literal["Euler", "RK4"]]
    comparison_mode: Literal["solo_numeric", "contra_analitica", "entre_metodos"] = "solo_numeric"

    # --- ÚNICO CAMBIO REALIZADO PARA ARREGLAR SWAGGER ---
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "EDO predefinida: crecimiento exponencial y' = λy",
                    "description": "Ejemplo con solución analítica para comparar Euler vs RK4.",
                    "value": {
                        "equation": {
                            "type": "predefined",
                            "id": "exp_growth",
                            "params": {"lambda": -2.0}
                        },
                        "initial_condition": {"x0": 0.0, "y0": 1.0},
                        "domain": {"x_end": 5.0},
                        "step": 0.1,
                        "methods": ["Euler", "RK4"],
                        "comparison_mode": "contra_analitica"
                    }
                },
                {
                    "summary": "EDO custom: ejemplo sin solución analítica",
                    "description": "Solo compara numéricamente Euler vs RK4.",
                    "value": {
                        "equation": {
                            "type": "custom",
                            "expression": "x*y - 2*x",
                            "variables": ["x", "y"]
                        },
                        "initial_condition": {"x0": 0.0, "y0": 1.0},
                        "domain": {"x_end": 3.0},
                        "step": 0.1,
                        "methods": ["Euler", "RK4"],
                        "comparison_mode": "entre_metodos"
                    }
                }
            ]
        }
    }


class MethodResultPoint(BaseModel):
    x: float
    y: float


class MethodMetadata(BaseModel):
    order: int
    num_steps: int
    compute_time_ms: float


class MethodResult(BaseModel):
    name: str
    points: List[MethodResultPoint]
    metadata: MethodMetadata


class AnalyticPoint(BaseModel):
    x: float
    y: float


class AnalyticSolution(BaseModel):
    expression: str
    points: List[AnalyticPoint]


class SimpleError(BaseModel):
    max: float
    rmse: float


class ErrorMetrics(BaseModel):
    vs_analytic: Optional[Dict[str, SimpleError]] = None
    between_methods: Optional[SimpleError] = None
    best_method: Optional[str] = None
    best_method_reason: Optional[str] = None


class ProblemSummary(BaseModel):
    equation_type: str
    equation_id: Optional[str] = None
    expression: Optional[str] = None
    x0: float
    y0: float
    x_end: float
    step: float
    num_points: int


class SolveResponse(BaseModel):
    problem_summary: ProblemSummary
    methods_results: List[MethodResult]
    analytic_solution: Optional[AnalyticSolution] = None
    error_metrics: Optional[ErrorMetrics] = None


class MethodInfo(BaseModel):
    name: str
    order: int


class ExampleProblem(BaseModel):
    id: str
    name: str
    equation_display: str
    default_params: Dict[str, float]
    default_initial_condition: InitialCondition
    default_domain: Domain
    suggested_step: float


# ============================================================
# 2. MOTOR NUMÉRICO (DOMINIO)
# ============================================================

def euler_solve(f, x0: float, y0: float, h: float, x_end: float):
    if h <= 0:
        raise ValueError("El paso h debe ser > 0")

    n_steps_real = (x_end - x0) / h
    n_steps = int(round(n_steps_real))

    if n_steps <= 0:
        raise ValueError("x_end debe ser mayor que x0 y consistente con h")

    xs = [x0]
    ys = [y0]
    x = x0
    y = y0

    for k in range(n_steps):
        y = y + h * f(x, y)
        x = x0 + (k + 1) * h
        xs.append(x)
        ys.append(y)

    return xs, ys


def rk4_solve(f, x0: float, y0: float, h: float, x_end: float):
    if h <= 0:
        raise ValueError("El paso h debe ser > 0")

    n_steps_real = (x_end - x0) / h
    n_steps = int(round(n_steps_real))

    if n_steps <= 0:
        raise ValueError("x_end debe ser mayor que x0 y consistente con h")

    xs = [x0]
    ys = [y0]
    x = x0
    y = y0

    for k in range(n_steps):
        k1 = f(x, y)
        k2 = f(x + h / 2.0, y + h * k1 / 2.0)
        k3 = f(x + h / 2.0, y + h * k2 / 2.0)
        k4 = f(x + h, y + h * k3)

        y = y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        x = x0 + (k + 1) * h
        xs.append(x)
        ys.append(y)

    return xs, ys


# ============================================================
# 3. ECUACIONES PREDEFINIDAS Y CUSTOM
# ============================================================

def get_predefined_f_and_analytic(eq: EquationInput, ic: InitialCondition):
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


# ============================================================
# 4. MÉTRICAS DE ERROR
# ============================================================

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


# ============================================================
# 5. SERVICIO PRINCIPAL
# ============================================================

def solve_and_compare(req: SolveRequest) -> SolveResponse:
    x0 = req.initial_condition.x0
    y0 = req.initial_condition.y0
    x_end = req.domain.x_end
    h = req.step

    if x_end <= x0:
        raise HTTPException(status_code=400, detail="x_end debe ser mayor que x0")

    f = None
    analytic_fn = None
    analytic_expr_str = None

    if req.equation.type == "predefined":
        try:
            f, analytic_fn, analytic_expr_str = get_predefined_f_and_analytic(
                req.equation, req.initial_condition
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        try:
            f = build_custom_f(req.equation)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if req.comparison_mode == "contra_analitica":
            raise HTTPException(
                status_code=400,
                detail="comparison_mode='contra_analitica' solo está soportado para ecuaciones predefinidas por ahora.",
            )

    methods_results: List[MethodResult] = []

    for method_name in req.methods:
        start = time.perf_counter()
        if method_name == "Euler":
            xs, ys = euler_solve(f, x0, y0, h, x_end)
            order = 1
        elif method_name == "RK4":
            xs, ys = rk4_solve(f, x0, y0, h, x_end)
            order = 4
        else:
            raise HTTPException(status_code=400, detail=f"Método no soportado: {method_name}")
        end = time.perf_counter()

        points = [MethodResultPoint(x=x, y=y) for x, y in zip(xs, ys)]
        metadata = MethodMetadata(
            order=order,
            num_steps=len(xs) - 1,
            compute_time_ms=(end - start) * 1000.0,
        )
        methods_results.append(
            MethodResult(
                name=method_name,
                points=points,
                metadata=metadata,
            )
        )

    num_points = len(methods_results[0].points) if methods_results else 0
    problem_summary = ProblemSummary(
        equation_type=req.equation.type,
        equation_id=req.equation.id,
        expression=req.equation.expression,
        x0=x0,
        y0=y0,
        x_end=x_end,
        step=h,
        num_points=num_points,
    )

    analytic_solution: Optional[AnalyticSolution] = None
    error_metrics: Optional[ErrorMetrics] = None

    if req.comparison_mode in ("contra_analitica", "entre_metodos") and analytic_fn is not None:
        xs_ref = [p.x for p in methods_results[0].points]
        ys_analytic = [analytic_fn(x) for x in xs_ref]

        analytic_points = [AnalyticPoint(x=x, y=y) for x, y in zip(xs_ref, ys_analytic)]
        analytic_solution = AnalyticSolution(
            expression=analytic_expr_str or "",
            points=analytic_points,
        )

        vs_analytic: Dict[str, SimpleError] = {}
        for mr in methods_results:
            ys_num = [p.y for p in mr.points]
            vs_analytic[mr.name] = compute_pointwise_errors(ys_num, ys_analytic)

        between_methods_err: Optional[SimpleError] = None
        if len(methods_results) >= 2:
            ys_m0 = [p.y for p in methods_results[0].points]
            ys_m1 = [p.y for p in methods_results[1].points]
            between_methods_err = compute_pointwise_errors(ys_m0, ys_m1)

        best_method = None
        best_rmse = None
        for name, err in vs_analytic.items():
            if best_rmse is None or err.rmse < best_rmse:
                best_rmse = err.rmse
                best_method = name

        best_reason = None
        if best_method is not None and best_rmse is not None:
            best_reason = f"{best_method} tiene el menor RMSE frente a la solución analítica."

        error_metrics = ErrorMetrics(
            vs_analytic=vs_analytic,
            between_methods=between_methods_err,
            best_method=best_method,
            best_method_reason=best_reason,
        )

    elif req.comparison_mode == "entre_metodos" and analytic_fn is None and len(methods_results) >= 2:
        ys_m0 = [p.y for p in methods_results[0].points]
        ys_m1 = [p.y for p in methods_results[1].points]
        between_methods_err = compute_pointwise_errors(ys_m0, ys_m1)

        names = [mr.name for mr in methods_results]
        best_method = "RK4" if "RK4" in names else names[0]
        best_reason = "RK4 es de orden 4 y normalmente más preciso que Euler para el mismo paso h."

        error_metrics = ErrorMetrics(
            vs_analytic=None,
            between_methods=between_methods_err,
            best_method=best_method,
            best_method_reason=best_reason,
        )

    return SolveResponse(
        problem_summary=problem_summary,
        methods_results=methods_results,
        analytic_solution=analytic_solution,
        error_metrics=error_metrics,
    )


# ============================================================
# 6. DATOS META MÍNIMOS
# ============================================================

METHODS_INFO: List[MethodInfo] = [
    MethodInfo(name="Euler", order=1),
    MethodInfo(name="RK4", order=4),
]

EXAMPLES: List[ExampleProblem] = [
    ExampleProblem(
        id="exp_growth",
        name="Crecimiento / decaimiento exponencial",
        equation_display="y' = λ y",
        default_params={"lambda": -2.0},
        default_initial_condition=InitialCondition(x0=0.0, y0=1.0),
        default_domain=Domain(x_end=5.0),
        suggested_step=0.1,
    )
]


# ============================================================
# 7. CAPA DE API (FASTAPI + SWAGGER)
# ============================================================

app = FastAPI(
    title="RK4 vs Euler Solver API",
    description="Motor numérico para EDO de primer orden (Euler y RK4).",
    version="0.1.0",
)


@app.get("/methods", response_model=List[MethodInfo], tags=["meta"])
def get_methods():
    return METHODS_INFO


@app.get("/examples", response_model=List[ExampleProblem], tags=["meta"])
def get_examples():
    return EXAMPLES


@app.post("/solve", response_model=SolveResponse, tags=["solver"])
def solve(req: SolveRequest):
    return solve_and_compare(req)
