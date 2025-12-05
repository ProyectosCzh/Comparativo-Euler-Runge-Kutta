from typing import List, Literal, Optional, Dict
from pydantic import BaseModel, Field


class EquationInput(BaseModel):
    """
    Representa la EDO en la entrada.
    El backend solo interpreta la ecuación (nada pedagógico).
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

    # Pydantic v2: swagger examples
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
