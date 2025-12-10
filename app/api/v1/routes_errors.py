# app/api/v1/routes_errors.py
from fastapi import APIRouter, HTTPException
from app.models.ode_requests import ErrorAnalysisRequest
from app.models.ode_responses import ErrorAnalysisResponse
from app.core.parser import parse_rhs
from app.services.euler_solver import euler_solver
from app.services.rk4_solver import rk4_solver
from app.services.analytic_solver import analytic_solver
from app.services.error_metrics import absolute_errors, summary_error_metrics

router = APIRouter()


def _run_full_solve(request: ErrorAnalysisRequest) -> ErrorAnalysisResponse:
    """
    Lógica central que:
      - Ejecuta Euler
      - Ejecuta RK4
      - Intenta resolver analíticamente
      - Calcula errores y métricas
    """
    try:
        f_sym, f_num = parse_rhs(request.f)

        # Euler
        grid_e, y_euler = euler_solver(f_num, request.t0, request.y0, request.T, request.h)

        # RK4 (mismo grid por construcción)
        grid_rk, y_rk4 = rk4_solver(f_num, request.t0, request.y0, request.T, request.h)

        if len(grid_e) != len(grid_rk):
            raise RuntimeError("Los grids de Euler y RK4 no coinciden, revise build_time_grid.")

        # Analítico
        grid_a, exact_values, meta_analytic = analytic_solver(
            f_sym, request.t0, request.y0, request.T, request.h
        )

        if len(grid_e) != len(grid_a):
            raise RuntimeError("El grid analítico no coincide con los numéricos, revise build_time_grid.")

        # Errores punto a punto
        errors_euler = absolute_errors(y_euler, exact_values)
        errors_rk4 = absolute_errors(y_rk4, exact_values)

        # Métricas resumen
        metrics_euler = summary_error_metrics(y_euler, exact_values)
        metrics_rk4 = summary_error_metrics(y_rk4, exact_values)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        # Lo relanzamos tal cual
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en comparación: {e}")

    meta = {
        "ode_simplified": meta_analytic.get("ode_simplified"),
        "exact_solution_latex": meta_analytic.get("exact_solution_latex"),
        "analytic_status": meta_analytic.get("analytic_status"),
        "convergence_order_euler": 1,
        "convergence_order_rk4": 4,
    }

    return ErrorAnalysisResponse(
        grid=grid_e,
        euler=y_euler,
        rk4=y_rk4,
        exact=exact_values,
        errors={
            "euler": errors_euler,
            "rk4": errors_rk4
        },
        error_metrics={
            "euler": metrics_euler,
            "rk4": metrics_rk4
        },
        meta=meta
    )


@router.post(
    "/errors",
    response_model=ErrorAnalysisResponse,
    summary="Comparar métodos y calcular errores",
    description=(
        "Calcula la solución aproximada por Euler y RK4, intenta obtener la solución analítica "
        "y devuelve los errores absolutos |y_num - y_exact| y métricas de error (máximo y RMSE)."
    ),
)
def compare_methods_and_errors(request: ErrorAnalysisRequest):
    return _run_full_solve(request)


@router.post(
    "/solve",
    response_model=ErrorAnalysisResponse,
    summary="Resolver EDO y obtener comparación completa (endpoint único)",
    description=(
        "Endpoint único pensado para el frontend: ejecuta Euler, RK4, intenta resolver analíticamente "
        "y devuelve soluciones, errores y métricas resumen en una sola respuesta."
    ),
)
def solve_all(request: ErrorAnalysisRequest):
    return _run_full_solve(request)
