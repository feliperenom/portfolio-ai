import os
import uuid
import getpass
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from classes import State, ChatRequest, ChatResponse, CustomToolNode
from rag import retriever_tool
from web_search import setup_web_search_tool
from langchain_openai import ChatOpenAI

# Configuración inicial
load_dotenv()

# Configurar API Keys
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")
_set_env("TAVILY_API_KEY")

# Inicializar componentes
llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125")
web_search_tool = setup_web_search_tool()

# Configurar el grafo
tools = [web_search_tool, retriever_tool]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Configurar FastAPI
app = FastAPI(title="FutureSmart AI Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Construir grafo una sola vez al iniciar
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", CustomToolNode(tools))
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        responses = []
        tools_used = []  # <-- NUEVA LISTA PARA ALMACENAR HERRAMIENTAS

        for event in graph.stream({"messages": [("user", request.message)]}, config):
            for value in event.values():
                if "messages" in value and value["messages"]:
                    responses.append(value["messages"][-1].content)
                
                # Si el estado incluye la lista de herramientas usadas, la agregamos
                if "tools_used" in value:
                    for tool_name in value["tools_used"]:
                        if tool_name not in tools_used:
                            tools_used.append(tool_name)

        # Devolvemos también la lista de herramientas (o None si está vacía)
        return ChatResponse(
            response=responses[-1] if responses else "No response generated",
            tools_used=tools_used if tools_used else None
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )