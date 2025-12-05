from typing import Any
from typing import List, Optional, Dict
import time

from fastapi import HTTPException

from app.schemas.ode_schemas import (
    SolveRequest,
    SolveResponse,
    MethodResultPoint,
    MethodMetadata,
    MethodResult,
    AnalyticSolution,
    AnalyticPoint,
    ProblemSummary,
    ErrorMetrics,
)
from app.domain.equations import get_predefined_f_and_analytic, build_custom_f
from app.domain.numerics.euler import euler_solve
from app.domain.numerics.rk4 import rk4_solve
from app.services.comparison_service import compute_pointwise_errors


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

    # Comparación con analítica (si existe)
    if req.comparison_mode in ("contra_analitica", "entre_metodos") and analytic_fn is not None:
        xs_ref = [p.x for p in methods_results[0].points]
        ys_analytic = [analytic_fn(x) for x in xs_ref]

        analytic_points = [AnalyticPoint(x=x, y=y) for x, y in zip(xs_ref, ys_analytic)]
        analytic_solution = AnalyticSolution(
            expression=analytic_expr_str or "",
            points=analytic_points,
        )

        vs_analytic: Dict[str, Any] = {}
        for mr in methods_results:
            ys_num = [p.y for p in mr.points]
            vs_analytic[mr.name] = compute_pointwise_errors(ys_num, ys_analytic)

        between_methods_err = None
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

    # Solo comparación entre métodos (sin analítica)
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
