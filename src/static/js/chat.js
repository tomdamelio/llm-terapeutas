// Elementos del DOM
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const analysisContainer = document.getElementById('analysis-container');
const analysisContent = document.getElementById('analysis-content');
const conversationHistory = document.getElementById('conversation-history');

// Variables de estado
let currentQuestionId = null;

// Función para añadir un mensaje al chat
function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Función para habilitar/deshabilitar la entrada
function setInputEnabled(enabled) {
    userInput.disabled = !enabled;
    sendButton.disabled = !enabled;
    if (enabled) {
        userInput.focus();
    }
}

// Función para mostrar el análisis
function showAnalysis(analysis) {
    let html = `
        <div class="urgency urgency-${analysis.urgency_level.toLowerCase()}">
            Nivel de Urgencia: ${analysis.urgency_level}
        </div>
        
        <h3>Áreas principales de preocupación:</h3>
        <ul>
            ${analysis.main_concerns.map(concern => `<li>${concern}</li>`).join('')}
        </ul>
        
        <h3>Recomendaciones:</h3>
        <ul>
            ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
        </ul>
    `;
    
    if (analysis.risk_factors && analysis.risk_factors.length > 0) {
        html += `
            <h3>Factores de riesgo:</h3>
            <ul>
                ${analysis.risk_factors.map(factor => `<li>${factor}</li>`).join('')}
            </ul>
        `;
    }
    
    if (analysis.protective_factors && analysis.protective_factors.length > 0) {
        html += `
            <h3>Factores protectores:</h3>
            <ul>
                ${analysis.protective_factors.map(factor => `<li>${factor}</li>`).join('')}
            </ul>
        `;
    }
    
    analysisContent.innerHTML = html;
    analysisContainer.style.display = 'block';
}

// Función para cargar el historial
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.status === 'success') {
            conversationHistory.innerHTML = data.conversations.map(conv => `
                <div class="conversation-item" onclick="loadConversation('${conv.conversation_id}')">
                    <div>ID: ${conv.conversation_id}</div>
                    <div>Fecha: ${new Date(conv.timestamp).toLocaleString()}</div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error al cargar el historial:', error);
    }
}

// Función para cargar una conversación específica
async function loadConversation(conversationId) {
    try {
        const response = await fetch(`/api/conversation/${conversationId}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            // Limpiar el chat actual
            chatMessages.innerHTML = '';
            
            // Mostrar las preguntas y respuestas
            const conversation = data.conversation;
            for (const [questionId, response] of Object.entries(conversation.responses)) {
                // Aquí deberías obtener la pregunta original usando el questionId
                addMessage(`Pregunta ${questionId}`, false);
                addMessage(response, true);
            }
            
            // Mostrar el análisis
            if (conversation.analysis) {
                showAnalysis(conversation.analysis);
            }
        }
    } catch (error) {
        console.error('Error al cargar la conversación:', error);
    }
}

// Función para iniciar una nueva conversación
async function startConversation() {
    try {
        const response = await fetch('/api/start', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            currentQuestionId = data.question_id;
            addMessage(data.question);
            setInputEnabled(true);
        }
    } catch (error) {
        console.error('Error al iniciar la conversación:', error);
    }
}

// Función para enviar un mensaje
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    addMessage(message, true);
    setInputEnabled(false);
    userInput.value = '';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                response: message,
                question_id: currentQuestionId
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            if (data.finished) {
                showAnalysis(data.analysis);
                loadHistory(); // Actualizar el historial
            } else {
                currentQuestionId = data.question_id;
                addMessage(data.question);
                setInputEnabled(true);
            }
        }
    } catch (error) {
        console.error('Error al enviar mensaje:', error);
        setInputEnabled(true);
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    startConversation();
    loadHistory();
}); 