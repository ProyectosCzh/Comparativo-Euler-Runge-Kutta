# app/models/ode_responses.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class EulerResponse(BaseModel):
    grid: List[float] = Field(..., description="Puntos de tiempo t_n.")
    euler: List[float] = Field(..., description="Aproximaciones y_n obtenidas por Euler.")
    meta: Dict[str, float] = Field(
        ...,
        description="Metadatos (ej: orden de convergencia)."
    )


class RK4Response(BaseModel):
    grid: List[float] = Field(..., description="Puntos de tiempo t_n.")
    rk4: List[float] = Field(..., description="Aproximaciones y_n obtenidas por RK4.")
    meta: Dict[str, float] = Field(
        ...,
        description="Metadatos (ej: orden de convergencia)."
    )

class AnalyticResponse(BaseModel):
    grid: List[float] = Field(..., description="Puntos de tiempo t_n.")
    exact: Optional[List[float]] = Field(
        None,
        description="Valores de la solución analítica y_exact(t_n). Puede ser null si no se pudo resolver."
    )
    meta: Dict[str, Any] = Field(
        ...,
        description="Información simbólica y estado de la solución analítica."
    )


class ErrorAnalysisResponse(BaseModel):
    grid: List[float] = Field(..., description="Puntos de tiempo t_n.")
    euler: List[float] = Field(..., description="Aproximaciones por Euler.")
    rk4: List[float] = Field(..., description="Aproximaciones por RK4.")
    exact: Optional[List[float]] = Field(
        None,
        description="Solución analítica evaluada, si está disponible."
    )
    errors: Dict[str, Optional[List[float]]] = Field(
        ...,
        description="Errores absolutos por método (euler, rk4)."
    )
    error_metrics: Dict[str, Optional[Dict[str, Optional[float]]]] = Field(
        ...,
        description="Métricas resumen de error por método: max y rmse."
    )
    meta: Dict[str, Any] = Field(
        ...,
        description="Información adicional: latex, estado de la solución, orden de métodos, etc."
    )
