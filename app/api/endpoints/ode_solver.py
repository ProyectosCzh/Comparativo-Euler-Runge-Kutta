from fastapi import APIRouter

from app.schemas.ode_schemas import (
    EulerRequest,
    EulerResponse,
    RK4Request,
    RK4Response,
    AnalyticRequest,
    AnalyticResponse,
    CompareRequest,
    CompareResponse,
)
from app.services.solver_service import (
    solve_euler,
    solve_rk4,
    solve_analytic,
    solve_benchmark,
)

router = APIRouter(prefix="/solve", tags=["solver"])


@router.post("/euler", response_model=EulerResponse)
def solve_with_euler(req: EulerRequest):
    """
    Resuelve la EDO usando exclusivamente el método de Euler.
    """
    return solve_euler(req)


@router.post("/rk4", response_model=RK4Response)
def solve_with_rk4(req: RK4Request):
    """
    Resuelve la EDO usando exclusivamente el método RK4.
    """
    return solve_rk4(req)


@router.post("/analytic", response_model=AnalyticResponse)
def solve_analytic_endpoint(req: AnalyticRequest):
    """
    Obtiene la solución analítica (si existe) y la muestrea en el intervalo.
    """
    return solve_analytic(req)


@router.post("/compare", response_model=CompareResponse)
def compare_methods(req: CompareRequest):
    """
    Ejecuta múltiples métodos (Euler, RK4) y los compara entre sí
    y/o contra la solución analítica (si aplica).
    """
    return solve_benchmark(req)
