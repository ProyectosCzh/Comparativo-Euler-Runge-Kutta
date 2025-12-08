from typing import List, Literal, Optional, Dict
from pydantic import BaseModel, Field


# ==========================
#  COMPARTIDOS
# ==========================

class EquationInput(BaseModel):
    """
    Representa la EDO en la entrada.
    """
    type: Literal["predefined", "custom"]
    id: Optional[Literal["exp_growth"]] = None  # por ahora solo esta predefinida
    params: Dict[str, float] = Field(default_factory=dict)

    # Para custom:
    expression: Optional[str] = None  # ej: "x*y - 2*x"
    variables: Optional[List[str]] = None  # normalmente ["x", "y"]


class InitialCondition(BaseModel):
    x0: float
    y0: float


class Domain(BaseModel):
    x_end: float


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


# ==========================
#  A) EULER
# ==========================

class EulerRequest(BaseModel):
    equation: EquationInput
    initial_condition: InitialCondition
    domain: Domain
    step: float = Field(gt=0, description="Tamaño de paso h > 0")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Euler con EDO predefinida",
                    "description": "y' = λy con λ = -2, x ∈ [0, 5], h = 0.1",
                    "value": {
                        "equation": {
                            "type": "predefined",
                            "id": "exp_growth",
                            "params": {"lambda": -2.0}
                        },
                        "initial_condition": {"x0": 0.0, "y0": 1.0},
                        "domain": {"x_end": 5.0},
                        "step": 0.1
                    }
                }
            ]
        }
    }


class EulerResponse(BaseModel):
    method: str  # "Euler"
    points: List[MethodResultPoint]
    metadata: MethodMetadata
    problem_summary: ProblemSummary


# ==========================
#  B) RK4
# ==========================

class RK4Request(BaseModel):
    equation: EquationInput
    initial_condition: InitialCondition
    domain: Domain
    step: float = Field(gt=0, description="Tamaño de paso h > 0")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "RK4 con EDO predefinida",
                    "description": "y' = λy con λ = -2, x ∈ [0, 5], h = 0.1",
                    "value": {
                        "equation": {
                            "type": "predefined",
                            "id": "exp_growth",
                            "params": {"lambda": -2.0}
                        },
                        "initial_condition": {"x0": 0.0, "y0": 1.0},
                        "domain": {"x_end": 5.0},
                        "step": 0.1
                    }
                }
            ]
        }
    }


class RK4Response(BaseModel):
    method: str  # "RK4"
    points: List[MethodResultPoint]
    metadata: MethodMetadata
    problem_summary: ProblemSummary


# ==========================
#  C) ANALÍTICA
# ==========================

class AnalyticRequest(BaseModel):
    """
    Solo tiene sentido para ecuaciones predefinidas,
    pero usamos EquationInput y validamos en el servicio.
    """
    equation: EquationInput
    initial_condition: InitialCondition
    domain: Domain
    step: float = Field(gt=0, description="Tamaño de paso h > 0 (para muestreo de puntos)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Solución analítica de y' = λy",
                    "description": "Muestra la curva analítica muestreada en [0,5] con h=0.1",
                    "value": {
                        "equation": {
                            "type": "predefined",
                            "id": "exp_growth",
                            "params": {"lambda": -2.0}
                        },
                        "initial_condition": {"x0": 0.0, "y0": 1.0},
                        "domain": {"x_end": 5.0},
                        "step": 0.1
                    }
                }
            ]
        }
    }


class AnalyticResponse(BaseModel):
    solution: AnalyticSolution
    problem_summary: ProblemSummary


# ==========================
#  D) COMPARADOR (BENCHMARK)
# ==========================

class CompareRequest(BaseModel):
    equation: EquationInput
    initial_condition: InitialCondition
    domain: Domain
    step: float = Field(gt=0, description="Tamaño de paso h > 0")
    methods: List[Literal["Euler", "RK4"]]
    comparison_mode: Literal["solo_numeric", "contra_analitica", "entre_metodos"] = "solo_numeric"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Comparar Euler vs RK4 contra analítica",
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
                    "summary": "Comparar Euler vs RK4 (sin analítica) con ecuación custom",
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


class CompareResponse(BaseModel):
    problem_summary: ProblemSummary
    methods_results: List[MethodResult]
    analytic_solution: Optional[AnalyticSolution] = None
    error_metrics: Optional[ErrorMetrics] = None
