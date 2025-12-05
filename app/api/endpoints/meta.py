from typing import List

from fastapi import APIRouter

from app.schemas.meta_schemas import MethodInfo, ExampleProblem
from app.schemas.ode_schemas import InitialCondition, Domain

router = APIRouter(tags=["meta"])

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


@router.get("/methods", response_model=List[MethodInfo])
def get_methods():
    return METHODS_INFO


@router.get("/examples", response_model=List[ExampleProblem])
def get_examples():
    return EXAMPLES
