# 🤖 Configuración del Chat con IA

Este documento explica cómo configurar el chat con IA usando OpenRouter.

## ¿Qué es OpenRouter?

OpenRouter es una API unificada que te da acceso a múltiples modelos de IA:
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus
- **Google**: Gemini Pro
- **Meta**: Llama 3.1
- Y muchos más...

**Ventajas:**
- ✅ Un solo API key para todos los modelos
- ✅ Precios competitivos
- ✅ Fácil cambiar entre modelos
- ✅ Sin necesidad de múltiples cuentas

## 📋 Pasos de Configuración

### 1. Obtener API Key de OpenRouter

1. Ve a https://openrouter.ai/
2. Crea una cuenta (puedes usar Google/GitHub)
3. Ve a https://openrouter.ai/keys
4. Crea una nueva API key
5. Copia tu API key (se verá algo como `sk-or-v1-...`)

### 2. Agregar Créditos (Opcional)

OpenRouter funciona con pay-as-you-go:
1. Ve a https://openrouter.ai/credits
2. Agrega $5-$10 para empezar (es suficiente para muchas conversaciones)
3. Monitorea tu uso en https://openrouter.ai/activity

### 3. Configurar Variables de Entorno

Crea un archivo `.env` en la carpeta `Comparativo-Euler-Runge-Kutta`:

```bash
# Copia el ejemplo
cp .env.example .env
```

Edita `.env` y configura tu API key:

```bash
OPENROUTER_API_KEY=sk-or-v1-tu-api-key-aqui
OPENROUTER_MODEL=openai/gpt-4o
SITE_URL=http://localhost:5173
SITE_NAME=EDO Lab
```

### 4. Reiniciar el Backend

```bash
cd Comparativo-Euler-Runge-Kutta
uvicorn app.main:app --reload
```

¡Listo! El chat ya debería funcionar.

## 🎛️ Modelos Disponibles

Puedes cambiar el modelo editando `OPENROUTER_MODEL` en tu `.env`:

### Modelos Recomendados:

**Para mejor calidad (más caro):**
```bash
OPENROUTER_MODEL=openai/gpt-4o              # GPT-4 Optimized
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet # Claude 3.5 Sonnet
OPENROUTER_MODEL=google/gemini-pro-1.5       # Gemini Pro 1.5
```

**Para uso económico:**
```bash
OPENROUTER_MODEL=openai/gpt-3.5-turbo        # GPT-3.5 Turbo (muy barato)
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct # Llama 3.1 70B
OPENROUTER_MODEL=google/gemini-flash-1.5     # Gemini Flash (rápido y barato)
```

**Lista completa:** https://openrouter.ai/models

## 💰 Costos Estimados

Con GPT-4o:
- ~$0.005 por pregunta típica
- $5 = ~1000 preguntas
- $10 = ~2000 preguntas

Con GPT-3.5-turbo:
- ~$0.001 por pregunta
- $5 = ~5000 preguntas

## 🧪 Probar la Configuración

### 1. Verificar que el backend esté corriendo:
```bash
curl http://localhost:8000/api/v1/chat/health
```

Deberías ver:
```json
{
  "status": "ok",
  "service": "chat",
  "model": "openai/gpt-4o"
}
```

### 2. Probar el chat:
1. Abre http://localhost:5173/problems/biology/logistic_growth
2. Haz click en el botón flotante "Pregunta a la IA"
3. Escribe: "¿Qué significa esta ecuación?"
4. ¡Deberías recibir una respuesta!

## 🐛 Solución de Problemas

### Error: "OPENROUTER_API_KEY no está configurada"
- Asegúrate de que el archivo `.env` esté en la carpeta `Comparativo-Euler-Runge-Kutta`
- Verifica que la variable se llame exactamente `OPENROUTER_API_KEY`
- Reinicia el backend después de crear/editar `.env`

### Error: "Error al comunicarse con OpenRouter"
- Verifica que tu API key sea correcta
- Asegúrate de tener créditos en OpenRouter
- Verifica tu conexión a internet

### No aparece el botón de chat
- Asegúrate de estar en una página de problema (ej: `/problems/biology/logistic_growth`)
- Verifica que el frontend esté corriendo
- Revisa la consola del navegador por errores

### Respuestas lentas
- GPT-4 puede tardar 5-10 segundos en responder
- Considera usar GPT-3.5-turbo o Gemini Flash para respuestas más rápidas
- Cambia el modelo en `.env`

## 📊 Monitorear Uso

Ve a https://openrouter.ai/activity para:
- Ver cuántas requests has hecho
- Cuánto has gastado
- Qué modelos usaste
- Logs de todas las conversaciones

## 🔒 Seguridad

⚠️ **NUNCA** compartas tu API key
⚠️ **NUNCA** hagas commit del archivo `.env` a git
✅ El archivo `.gitignore` ya excluye `.env`
✅ Solo comparte `.env.example` (sin el API key real)
