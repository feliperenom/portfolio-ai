import asyncio
import os
import requests
import streamlit as st

# API URL
API_URL = "https://news-chatbot-back-119684997782.us-central1.run.app/chat/"

# Page configuration
st.set_page_config(
    page_title="News Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar with information
with st.sidebar:
    st.title("News Chatbot")
    st.markdown(
        """
        💡 **How does it work?**
        - Ask questions about recent news.
        - Get responses with links to reliable sources.
        - Learn about current events in real-time.

        📌 **Instructions:**
        - Type a message and press **Enter**.
        - Click the button to restart the conversation.
        """
    )

    if st.button("🔄 Restart Chat"):
        st.session_state.messages = []  # Clear the conversation
        st.rerun()

# Initialize the conversation if it does not exist in the session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat container
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"{msg['content']}", unsafe_allow_html=True)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"{msg['content']}", unsafe_allow_html=True)
                
                # Show links if available
                if "links" in msg:
                    for link in msg["links"]:
                        st.markdown(f"[🔗 Read more]({link})", unsafe_allow_html=True)

# Function to send a message
def send_message():
    user_message = st.session_state.user_input.strip()

    if user_message:
        response = requests.post(API_URL, json={
            "conversation_history": [m["content"] for m in st.session_state.messages],
            "user_input": user_message
        })

        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("conversation_history", [])[-1]
            links = data.get("links", [])

            # Store messages
            st.session_state.messages.append({"role": "user", "content": user_message})
            bot_msg = {"role": "assistant", "content": bot_response}

            if links:
                bot_msg["links"] = links

            st.session_state.messages.append(bot_msg)

            # Clear the input box
            st.session_state.user_input = ""

            # Reload the interface
            st.rerun()

# Input with automatic submission on "Enter"
user_input = st.chat_input("Type your message here...")
if user_input:
    st.session_state.user_input = user_input
    send_message()
