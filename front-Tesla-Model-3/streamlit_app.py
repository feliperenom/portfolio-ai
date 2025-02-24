import streamlit as st
import requests

api_url = "https://tesla-model-3-chatbot-back-119684997782.us-central1.run.app/chat"

# Configuración de la API
st.set_page_config(page_title="Chat with Tesla Model 3 User Manual", layout="wide")

# Sidebar para configuraciones
st.sidebar.title("Configuration")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
max_tokens = st.sidebar.slider("Max Tokens", 500, 4000, 2000, 500)

# Inicializar el estado de la conversación
if "messages" not in st.session_state:
    st.session_state.messages = []

# Título principal
st.title("💬 Chat with Tesla Model 3 User Manual")

# Mostrar mensajes previos
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada del usuario
prompt = st.chat_input("Type your message here...")

if prompt:
    # Mostrar mensaje del usuario en la conversación
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Enviar la consulta a la API
    try:
        response = requests.post(api_url, json={"prompt": prompt})
        response.raise_for_status()
        bot_reply = response.json().get("response", "Answer not found.")

    except requests.exceptions.RequestException as e:
        bot_reply = f"❌ Error in the API: {e}"

    # Mostrar respuesta del chatbot
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
