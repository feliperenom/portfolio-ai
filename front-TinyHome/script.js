const API_URL = 'http://127.0.0.1:8000/chat';
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loadingIndicator = document.getElementById('loading');

function appendMessage(message, isUser = false, tools = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    // Icono
    const icon = document.createElement('div');
    icon.className = 'message-icon';
    icon.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    // Contenido
    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = message.replace(/\n/g, '<br>');

    messageDiv.appendChild(icon);
    messageDiv.appendChild(content);

    // Herramientas usadas
    if (tools) {
        const toolsDiv = document.createElement('div');
        toolsDiv.className = 'tools-used';
        toolsDiv.innerHTML = `
            <i class="fas fa-tools"></i>
            Herramientas usadas: ${tools.join(', ')}
        `;
        messageDiv.appendChild(toolsDiv);
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    messageInput.value = '';
    sendButton.disabled = true;
    loadingIndicator.style.display = 'block';
    
    appendMessage(message, true);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        appendMessage(data.response, false, data.tools_used);
    } catch (error) {
        console.error('Error:', error);
        appendMessage('⚠️ Error al procesar tu solicitud. Por favor intenta nuevamente.', false);
    } finally {
        sendButton.disabled = false;
        loadingIndicator.style.display = 'none';
        messageInput.focus();
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
    
    // Autoajuste del textarea
    setTimeout(() => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    }, 0);
}

// Inicialización
messageInput.focus();
