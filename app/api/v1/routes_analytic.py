# app/api/v1/routes_analytic.py
from fastapi import APIRouter, HTTPException
from models.ode_requests import AnalyticRequest
from models.ode_responses import AnalyticResponse
from core.parser import parse_rhs
from services.analytic_solver import analytic_solver

router = APIRouter()


@router.post(
    "/analytic",
    response_model=AnalyticResponse,
    summary="Intentar resolver analíticamente la EDO",
    description=(
        "Intenta obtener la solución analítica de la EDO de primer orden y' = f(t, y) "
        "usando SymPy (dsolve). Devuelve la solución evaluada en el grid si es posible."
    ),
)
def solve_analytic(request: AnalyticRequest):
    """
    Intenta resolver analíticamente y' = f(t, y(t)) con y(t0)=y0.
    """
    try:
        f_sym, _ = parse_rhs(request.f)
        grid, exact_values, meta = analytic_solver(f_sym, request.t0, request.y0, request.T, request.h)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en analítico: {e}")

    return AnalyticResponse(
        grid=grid,
        exact=exact_values,
        meta=meta
    )
