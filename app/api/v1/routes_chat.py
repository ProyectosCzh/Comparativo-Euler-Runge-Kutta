# app/api/v1/routes_chat.py
from fastapi import APIRouter, HTTPException
from app.models.chat_models import ChatRequest, ChatResponse
from app.services.chat_service import get_chat_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Endpoint para chatear con IA sobre el problema actual.

    Recibe el mensaje del usuario, el contexto del problema,
    los parámetros de simulación y el historial de conversación.

    Retorna la respuesta de la IA con contexto del problema.
    """
    try:
        # Obtener el servicio de chat
        chat_service = get_chat_service()

        # Convertir los modelos Pydantic a diccionarios
        problem_context = request.problem_context.model_dump()
        parameters = request.parameters.model_dump()
        history = [msg.model_dump() for msg in request.history] if request.history else []

        # Obtener respuesta de la IA
        ai_response = chat_service.get_response(
            user_message=request.message,
            problem_context=problem_context,
            parameters=parameters,
            history=history
        )

        return ChatResponse(
            response=ai_response,
            success=True
        )

    except ValueError as ve:
        # Error de configuración (API key no configurada)
        raise HTTPException(
            status_code=500,
            detail=f"Error de configuración del servicio: {str(ve)}"
        )

    except Exception as e:
        # Otros errores
        return ChatResponse(
            response="",
            success=False,
            error=f"Error al procesar tu pregunta: {str(e)}"
        )


@router.get("/chat/health")
async def check_chat_health():
    """
    Endpoint para verificar si el servicio de chat está disponible.
    """
    try:
        chat_service = get_chat_service()
        return {
            "status": "ok",
            "service": "chat",
            "model": chat_service.model
        }
    except ValueError as ve:
        return {
            "status": "error",
            "service": "chat",
            "error": str(ve)
        }
