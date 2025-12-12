# app/api/v1/routes_euler.py
from fastapi import APIRouter, HTTPException
from app.models.ode_requests import ODEBaseRequest
from app.models.ode_responses import EulerResponse
from app.core.parser import parse_rhs
from app.services.euler_solver import euler_solver

router = APIRouter()


@router.post(
    "/euler",
    response_model=EulerResponse,
    summary="Resolver EDO con método de Euler",
    description=(
        "Resuelve una ecuación diferencial ordinaria de primer orden de la forma "
        "y' = f(t, y) usando el método de Euler explícito."
    ),
)
def solve_euler(request: ODEBaseRequest):
    """
    Calcula la solución numérica usando Euler.
    """
    try:
        f_sym, f_num = parse_rhs(request.f)
        grid, y_values = euler_solver(f_num, request.t0, request.y0, request.T, request.h)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en Euler: {e}")

    meta = {
        "convergence_order": 1,
    }

    return EulerResponse(
        grid=grid,
        euler=y_values,
        meta=meta
    )
