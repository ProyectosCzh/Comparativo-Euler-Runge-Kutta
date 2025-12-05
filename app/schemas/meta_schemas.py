from typing import Dict
from pydantic import BaseModel
from .ode_schemas import InitialCondition, Domain


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
