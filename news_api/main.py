from fastapi import FastAPI
from pydantic import BaseModel
from get_news import chat_with_bot  # Importamos la función del agente

# Inicializar la aplicación FastAPI
app = FastAPI()

# Modelo de datos para la solicitud de la API
class ChatRequest(BaseModel):
    conversation_history: list[str]  # Historial de mensajes previos
    user_input: str  # Entrada del usuario

# Endpoint para interactuar con el chatbot
@app.post("/chat/")
async def chat_with_news_bot(request: ChatRequest):
    try:
        updated_conversation = chat_with_bot(request.conversation_history, request.user_input)

        # Extraer la respuesta del bot
        bot_response = updated_conversation[-1]  # Último mensaje del bot

        # Si el bot pregunta algo en vez de responder con noticias, forzamos la búsqueda de noticias
        if "¿Qué tipo de noticias" in bot_response or "¿Hay alguna región" in bot_response:
            bot_response = "Aquí tienes las últimas noticias relacionadas con tu consulta:\n" + get_latest_news(request.user_input)

        # Extraer enlaces si están en la respuesta
        links = [word for word in bot_response.split() if word.startswith("http")]

        return {"conversation_history": updated_conversation, "links": links}
    except Exception as e:
        return {"error": str(e)}

# Mensaje de bienvenida
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API del Chatbot de Noticias AI. Usa /chat/ para interactuar con el agente."}
