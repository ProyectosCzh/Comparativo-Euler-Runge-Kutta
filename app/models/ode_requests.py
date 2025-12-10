# app/models/ode_requests.py
from pydantic import BaseModel, Field
from typing import Optional


class ODEBaseRequest(BaseModel):
    """
    Request base para una EDO de primer orden y' = f(t, y).
    """
    f: str = Field(
        ...,
        description="Expresión de f(t, y) en formato SymPy. Ej: 't*y + 2', 'sin(t) - y'."
    )
    t0: float = Field(..., description="Valor inicial de t (punto de inicio del intervalo).")
    y0: float = Field(..., description="Condición inicial y(t0) = y0.")
    T: float = Field(..., description="Extremo derecho del intervalo de integración.")
    h: float = Field(..., gt=0, description="Paso de integración (tamaño de paso).")

    class Config:
        schema_extra = {
            "example": {
                "f": "t*y + 2",
                "t0": 0.0,
                "y0": 1.0,
                "T": 5.0,
                "h": 0.1
            }
        }


class AnalyticRequest(ODEBaseRequest):
    """
    Request para la solución analítica.
    Por ahora, es igual al base, pero lo separamos por claridad.
    """
    pass


class ErrorAnalysisRequest(ODEBaseRequest):
    """
    Request para el endpoint de errores / comparación.
    Se podría extender (ej: elegir qué métodos comparar),
    pero por ahora usa Euler, RK4 y analítico.
    """
    # En el futuro aquí podrías activar/desactivar métodos, etc.
    pass
