import streamlit as st
import requests
import os

# Configuración de la API
API_URL = "http://localhost:8000/chat"  # Asegúrate que la API esté corriendo

# Configurar título de la página
st.set_page_config(
    page_title="Canada Info AI Chat",
    page_icon="🤖",
    layout="centered"
)

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de chat
# --------------------------------------------------------------------
# Al recorrer los mensajes guardados, mostramos el texto de cada uno
# y, si existe, las herramientas que se usaron.
# --------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Mostrar las herramientas utilizadas, si existen
        if "tools_used" in message and message["tools_used"]:
            st.markdown(
                f"**Herramientas utilizadas:** {', '.join(message['tools_used'])}"
            )

# Función para obtener respuestas de la API
# --------------------------------------------------------------------
# Ahora retornamos tanto el texto de la respuesta como la lista
# de herramientas usadas (tools_used).
# --------------------------------------------------------------------
def get_ai_response(user_input):
    try:
        response = requests.post(
            API_URL,
            json={"message": user_input},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            ai_text = data.get("response", "")
            tools_used = data.get("tools_used", [])
            return ai_text, tools_used
        else:
            return f"Error: {response.text}", []
    except Exception as e:
        return f"Error de conexión: {str(e)}", []

# Interfaz de entrada de usuario
# --------------------------------------------------------------------
# Al enviar un mensaje, pedimos la respuesta de la IA y también
# la lista de herramientas. Guardamos ambos en el historial.
# --------------------------------------------------------------------
if prompt := st.chat_input("Escribe tu pregunta..."):
    # Añade mensaje de usuario a historial
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Muestra mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)

    # Llama a la API y obtiene (texto_respuesta, herramientas_usadas)
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            ai_response, tools_used = get_ai_response(prompt)
            
            st.markdown(ai_response)

            # Muestra las herramientas en la interfaz
            if tools_used:
                st.markdown(
                    f"**Herramientas utilizadas:** {', '.join(tools_used)}"
                )

    # Guarda también las herramientas en el historial (si quieres conservarlo)
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_response,
        "tools_used": tools_used
    })

