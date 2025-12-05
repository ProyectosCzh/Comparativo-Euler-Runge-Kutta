from fastapi import APIRouter

from app.schemas.ode_schemas import SolveRequest, SolveResponse
from app.services.solver_service import solve_and_compare

router = APIRouter(tags=["solver"])


@router.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    return solve_and_compare(req)
