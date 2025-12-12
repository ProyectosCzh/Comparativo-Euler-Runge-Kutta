# app/models/chat_models.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ProblemContext(BaseModel):
    """Contexto del problema actual"""
    problem_id: str = Field(..., description="ID del problema")
    problem_name: str = Field(..., description="Nombre del problema")
    category: str = Field(..., description="Categoría del problema")
    equation: str = Field(..., description="Ecuación diferencial")
    description: str = Field(..., description="Descripción del problema")
    theory: Optional[Dict[str, Any]] = Field(None, description="Fundamento teórico")


class SimulationParameters(BaseModel):
    """Parámetros de la simulación actual"""
    t0: float = Field(..., description="Valor inicial")
    y0: float = Field(..., description="Condición inicial")
    tf: float = Field(..., description="Valor final")
    h: float = Field(..., description="Tamaño de paso")


class ChatMessage(BaseModel):
    """Mensaje en el chat"""
    role: str = Field(..., description="'user' o 'assistant'")
    content: str = Field(..., description="Contenido del mensaje")


class ChatRequest(BaseModel):
    """Request para el endpoint de chat"""
    message: str = Field(..., description="Mensaje del usuario")
    problem_context: ProblemContext = Field(..., description="Contexto del problema actual")
    parameters: SimulationParameters = Field(..., description="Parámetros de simulación")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Historial de conversación")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "¿Por qué esta ecuación modela el crecimiento logístico?",
                "problem_context": {
                    "problem_id": "logistic_growth",
                    "problem_name": "Modelo de Crecimiento Logístico",
                    "category": "Biología",
                    "equation": "r*y*(1 - y/K)",
                    "description": "Modelo de crecimiento poblacional con capacidad de carga",
                    "theory": {}
                },
                "parameters": {
                    "t0": 0.0,
                    "y0": 10.0,
                    "tf": 50.0,
                    "h": 0.1
                },
                "history": []
            }
        }


class ChatResponse(BaseModel):
    """Response del endpoint de chat"""
    response: str = Field(..., description="Respuesta de la IA")
    success: bool = Field(default=True, description="Si la petición fue exitosa")
    error: Optional[str] = Field(None, description="Mensaje de error si hubo alguno")
