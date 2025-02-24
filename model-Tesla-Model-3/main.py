import os
import logging
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import Response, PlainTextResponse
from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI
from google.cloud import aiplatform
from fastapi.middleware.cors import CORSMiddleware
from retriever import retrieve_documents
import json
from classes import ChatRequest

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Obtener las variables del entorno
project_id = os.getenv("PROJECT_ID")
service_account_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

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

# Inicializar Vertex AI
try:
    aiplatform.init(project=project_id, location="us-central1")
except Exception as e:
    logging.error(f"Error al inicializar Vertex AI: {e}")
    raise

# Configurar el modelo Gemini-Pro en Vertex AI
try:
    chat_model = ChatVertexAI(model_name="gemini-pro", temperature=0.0, max_output_tokens=2000)
except Exception as e:
    logging.error(f"Error al cargar Gemini-Pro: {e}")
    raise

# Inicializar FastAPI
app = FastAPI()

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System Prompt
SYSTEM_PROMPT = """
Always answer only with what's conained in the PDF doc, and not your knowledge. 
If you don't find answers to the question, reply: "I couldn't find any answers for your question". 
Don't invent answers or hallucinate. Just answer with what's in the document. 
"""

@app.post("/chat")
def chat(request: ChatRequest):
    """
    Endpoint para recibir una consulta de usuario y devolver la respuesta del chatbot.
    """
    try:
        # Recuperar contexto relevante desde ChromaDB
        context = retrieve_documents(request.prompt) or "No se encontró información relevante en la base de datos."
        
        if "No se encontró información relevante" in context:
            context_text = "No se encontró información relevante en la base de datos."
        else:
            context_text = f"Usa la siguiente información para responder:\n\n{context}"

        # Construir el prompt con el System Prompt + contexto + pregunta
        full_prompt = f"{SYSTEM_PROMPT}\n\n{context_text}\n\nPregunta: {request.prompt}"

        # Pasar el prompt al modelo de Gemini-Pro
        try:
            response = chat_model.invoke(full_prompt)
            bot_reply = response.content if response else "No se pudo generar una respuesta."
        except Exception as e:
            logging.error(f"❌ Error en la invocación del modelo: {e}", exc_info=True)
            bot_reply = f"❌ Error: {str(e)}"

        return {"response": bot_reply}

    except Exception as e:
        logging.error(f"❌ Error en el endpoint /chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "API de chat con Gemini-Pro y RAG funcionando correctamente."}
