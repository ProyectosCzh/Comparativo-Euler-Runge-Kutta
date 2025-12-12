# app/api/v1/routes_rk4.py
from fastapi import APIRouter, HTTPException
from app.models.ode_requests import ODEBaseRequest
from app.models.ode_responses import RK4Response
from app.core.parser import parse_rhs
from app.services.rk4_solver import rk4_solver


router = APIRouter()


@router.post(
    "/rk4",
    response_model=RK4Response,
    summary="Resolver EDO con método de Runge-Kutta RK4",
    description=(
        "Resuelve una ecuación diferencial ordinaria de primer orden de la forma "
        "y' = f(t, y) usando el método clásico de Runge-Kutta de orden 4."
    ),
)
def solve_rk4(request: ODEBaseRequest):
    """
    Calcula la solución numérica usando RK4.
    """
    try:
        f_sym, f_num = parse_rhs(request.f)
        grid, y_values = rk4_solver(f_num, request.t0, request.y0, request.T, request.h)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en RK4: {e}")

    meta = {
        "convergence_order": 4,
    }

    return RK4Response(
        grid=grid,
        rk4=y_values,
        meta=meta
    )
