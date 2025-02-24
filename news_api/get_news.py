import os
import requests
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_vertexai import ChatVertexAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel
from typing import List

# 🔄 Cargar API Keys desde .env
load_dotenv()

# Obtener las variables del entorno
project_id = os.getenv("PROJECT_ID")
service_account_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
NEWS_API_KEY = os.getenv("newsapi_key")

# Verificar si las variables están cargadas correctamente
if not service_account_key or not project_id:
    raise ValueError("Las variables de entorno no están configuradas correctamente.")

# ───────────────────────────────────────────────────────────────
# ───────────────────────────────────────────────────────────────
# ───────────────────────────────────────────────────────────────
# Esta sección es para el deploy: guarda la clave JSON en un archivo temporal.
# En desarrollo, puedes configurar GOOGLE_APPLICATION_CREDENTIALS directamente.

credentials_path = "/tmp/service-account.json"

try:
     with open(credentials_path, "w") as f:
         f.write(service_account_key)
     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
except Exception as e:
     raise RuntimeError(f"Error al escribir el archivo de credenciales: {e}")
# ───────────────────────────────────────────────────────────────
# ───────────────────────────────────────────────────────────────
# ───────────────────────────────────────────────────────────────

if not NEWS_API_KEY or not project_id:
    raise ValueError("⚠️ No se encontraron las claves API en el archivo .env.")

# 🔍 Función para obtener noticias desde NewsAPI
def get_latest_news(query: str):
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get("articles", [])
        if articles:
            news_results = [f"{idx + 1}. {article['title']} - {article['url']}" for idx, article in enumerate(articles[:5])]
            return "\n".join(news_results)
        else:
            return "⚠️ I didn't find relevant news."
    else:
        return f"⚠️ Error getting news: {response.status_code}"

# 📌 Definir el estado del chatbot como un modelo de Pydantic
class ChatState(BaseModel):
    conversation: List[str] = []  # Historial de mensajes
    user_query: str
    news_response: str = ""

# 🎭 Nodo: Obtener noticias siempre
def fetch_news(state: ChatState):
    """Busca noticias siempre que el usuario haga una pregunta."""
    news = get_latest_news(state.user_query)
    state.news_response = news
    return state

# 🎭 Nodo: Responder con las noticias encontradas (mejor presentación)
def generate_response(state: ChatState):
    """El chatbot solo devuelve noticias sin repreguntar, con formato ordenado."""
    if state.news_response:
        articles = state.news_response.split("\n")
        formatted_news = "\n\n".join([f"**{idx+1}. {article.split(' - ')[0]}**\n🔗 [Leer más]({article.split(' - ')[1]})"
                                      for idx, article in enumerate(articles) if " - " in article])
        response_text = f"Here are the latest news:\n\n{formatted_news}"
    else:
        response_text = "⚠️ I didn't find news for your query."

    # Agregar la respuesta al historial
    state.conversation.append(f"🤖 {response_text}")
    return state


# 🏗️ Construcción del Grafo en LangGraph
workflow = StateGraph(ChatState)
workflow.add_node("fetch_news", fetch_news)
workflow.add_node("generate_response", generate_response)

# 🔗 Conectar los nodos
workflow.set_entry_point("fetch_news")
workflow.add_edge("fetch_news", "generate_response")  
workflow.add_edge("generate_response", END)

# 🚀 Compilar el Grafo
news_chatbot = workflow.compile()

# 🔥 Función para ejecutar el chatbot
def chat_with_bot(conversation_history: List[str], user_input: str):
    state = ChatState(conversation=conversation_history, user_query=user_input)
    result = news_chatbot.invoke(state)
    return result.get("conversation", [])  # ✅ Accedemos correctamente al historial

# ✅ Prueba del chatbot
if __name__ == "__main__":
    print("🤖 Chatbot de Noticias AI activado. Escribe 'salir' para terminar.")
    conversation_history = []

    while True:
        user_input = input("🧑 Tú: ")
        if user_input.lower() == "salir":
            break
        
        conversation_history = chat_with_bot(conversation_history, user_input)
        print(conversation_history[-1])  # Mostrar la última respuesta del bot
