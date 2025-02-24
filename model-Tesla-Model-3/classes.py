from pydantic import BaseModel

# Modelo para la solicitud
class ChatRequest(BaseModel):
    prompt: str