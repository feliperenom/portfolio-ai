from pydantic import BaseModel
from typing import Annotated, TypedDict, List, Optional
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

class RagToolSchema(BaseModel):
    question: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    tools_used: Optional[List[str]] = None   

class State(TypedDict):
    messages: Annotated[list, add_messages]

class CustomToolNode(ToolNode):
    """
    Subclase de ToolNode que intercepta la ejecución de la herramienta
    y guarda el nombre en el state.
    """
    def run(self, state, config):
        # Ejecuta la lógica original
        result = super().run(state, config)

        # Intenta obtener el nombre de la herramienta
        tool_name = getattr(self.tool, "name", None)

        # Guarda la herramienta en state["tools_used"]
        if tool_name:
            if "tools_used" not in state:
                state["tools_used"] = []
            if tool_name not in state["tools_used"]:
                state["tools_used"].append(tool_name)

        return result