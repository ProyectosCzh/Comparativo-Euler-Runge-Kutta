# app/services/chat_service.py
import os
import requests
import json
from typing import List, Dict


class ChatService:
    """Servicio para manejar chat con IA usando OpenRouter"""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY no está configurada. "
                "Configura la variable de entorno con tu API key de OpenRouter."
            )

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")
        self.site_url = os.getenv("SITE_URL", "http://localhost:5173")
        self.site_name = os.getenv("SITE_NAME", "EDO Lab")

    def build_system_prompt(self, problem_context: Dict, parameters: Dict) -> str:
        """Construye el prompt del sistema con el contexto del problema"""

        theory_text = ""
        if problem_context.get("theory"):
            theory = problem_context["theory"]
            if theory.get("origin"):
                theory_text += f"\n\nOrigen: {theory['origin']}"
            if theory.get("derivation"):
                theory_text += "\n\nDerivación matemática:"
                for step in theory["derivation"]:
                    if step.get("text"):
                        theory_text += f"\n- {step['text']}"
                    if step.get("latex"):
                        theory_text += f"\n- Ecuación: {step['latex']}"
            if theory.get("applications"):
                theory_text += "\n\nAplicaciones:"
                for app in theory["applications"]:
                    theory_text += f"\n- {app}"

        system_prompt = f"""Eres un asistente educativo experto en ecuaciones diferenciales ordinarias (EDOs).
Estás ayudando a un estudiante que está trabajando con el siguiente problema:

**Problema: {problem_context.get('problem_name', 'N/A')}**
Categoría: {problem_context.get('category', 'N/A')}

**Ecuación Diferencial:**
dy/dx = {problem_context.get('equation', 'N/A')}

**Descripción:**
{problem_context.get('description', 'N/A')}

**Fundamento Teórico:**{theory_text if theory_text else ' No disponible'}

**Parámetros Actuales de la Simulación:**
- Valor inicial (x₀): {parameters.get('t0', 'N/A')}
- Condición inicial (y₀): {parameters.get('y0', 'N/A')}
- Valor final (xf): {parameters.get('tf', 'N/A')}
- Tamaño de paso (h): {parameters.get('h', 'N/A')}

Tu objetivo es:
1. Ayudar al estudiante a entender el problema y sus conceptos
2. Explicar la ecuación diferencial y su significado físico/biológico
3. Aclarar dudas sobre los parámetros y cómo afectan la solución
4. Explicar conceptos matemáticos de forma clara y didáctica
5. Proporcionar intuición sobre el comportamiento de la solución
6. Responder preguntas sobre métodos numéricos (Euler, Runge-Kutta)

Instrucciones:
- Sé conciso pero claro
- Usa ejemplos cuando sea apropiado
- Si el estudiante pregunta sobre los parámetros, refiere los valores actuales
- Puedes usar notación matemática en formato LaTeX cuando sea necesario (usa $ para inline)
- Enfócate en la comprensión conceptual, no solo en fórmulas
- Si es apropiado, sugiere experimentos cambiando parámetros
"""
        return system_prompt

    def get_response(
        self,
        user_message: str,
        problem_context: Dict,
        parameters: Dict,
        history: List[Dict] = None
    ) -> str:
        """Obtiene respuesta de la IA con el contexto del problema"""

        system_prompt = self.build_system_prompt(problem_context, parameters)

        # Construir mensajes para la API
        messages = []

        # Agregar prompt del sistema como primer mensaje
        messages.append({
            "role": "system",
            "content": system_prompt
        })

        # Agregar historial si existe
        if history:
            for msg in history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Agregar mensaje actual del usuario
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Llamar a la API de OpenRouter
        try:
            response = requests.post(
                url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": self.site_url,
                    "X-Title": self.site_name,
                    "Content-Type": "application/json"
                },
                data=json.dumps({
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.7
                })
            )

            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error al comunicarse con OpenRouter: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Error al procesar la respuesta de OpenRouter: {str(e)}")


# Instancia global del servicio (se inicializa una vez)
_chat_service = None


def get_chat_service() -> ChatService:
    """Obtiene la instancia del servicio de chat (singleton)"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
