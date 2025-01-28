// Variables globales
let isAnalysisComplete = false;
let isWaitingForResponse = false;

// Elementos del DOM
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const analysisContainer = document.getElementById('analysis-container');
const analysisContent = document.getElementById('analysis-content');
const conversationHistory = document.getElementById('conversation-history');

// Variables de estado
let currentQuestionId = null;

// Mapeo de IDs de preguntas a sus textos
const QUESTION_MAP = {
    "main_concern": "¿Cuál es el principal motivo por el que buscas ayuda hoy?",
    "duration": "¿Hace cuánto tiempo te sientes así?",
    "daily_impact": "¿Cómo afecta esto tu vida diaria (trabajo, relaciones, actividades)?",
    "mood_changes": "¿Has notado cambios significativos en tu estado de ánimo recientemente?",
    "sleep": "¿Cómo ha estado tu sueño últimamente?",
    "support": "¿Tienes personas cercanas que te apoyen en este momento?",
    "previous_help": "¿Has buscado ayuda profesional anteriormente?",
    "self_harm": "¿Has tenido pensamientos de hacerte daño?",
    "substance_use": "¿Has aumentado el consumo de alcohol u otras sustancias?",
    "coping_mechanisms": "¿Qué haces cuando te sientes así? ¿Qué te ayuda?"
};

// Función para crear el indicador de escritura
function createTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'typing-indicator';
    indicator.textContent = 'Escribiendo...';
    return indicator;
}

// Función para mostrar/ocultar el indicador de escritura
function showTypingIndicator(show = true) {
    let typingIndicator = document.getElementById('typing-indicator');
    
    if (show && !typingIndicator) {
        typingIndicator = createTypingIndicator();
        chatMessages.appendChild(typingIndicator);
    } else if (!show && typingIndicator) {
        typingIndicator.remove();
    }
    
    if (typingIndicator) {
        typingIndicator.style.display = show ? 'block' : 'none';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Función para simular el delay de escritura
function simulateTypingDelay(message) {
    return new Promise(resolve => {
        showTypingIndicator(true);
        setTimeout(() => {
            showTypingIndicator(false);
            resolve(message);
        }, 1000);
    });
}

// Función para añadir un mensaje al chat
async function addMessage(message, isUser = false) {
    if (!message) return;

    if (!isUser) {
        message = await simulateTypingDelay(message);
    }

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
    analysisContainer.style.display = 'block';
    
    let html = `
        <div class="urgency urgency-${analysis.urgency_level.toLowerCase()}">
            Nivel de Urgencia: ${analysis.urgency_level}
        </div>
        
        <h3>Áreas principales de preocupación:</h3>
        <ul>
            ${analysis.main_concerns.map(concern => `<li>${concern}</li>`).join('')}
        </ul>
        
        <h3>Diagnósticos preliminares:</h3>
        <ul>
            ${analysis.preliminary_diagnoses.map(diagnosis => `
                <li>
                    <strong>${diagnosis.condition}</strong> (Confianza: ${diagnosis.confidence})
                    <br>
                    <small>Indicadores clave: ${diagnosis.key_indicators.join(', ')}</small>
                </li>
            `).join('')}
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

    html += `
        <h3>Recomendaciones:</h3>
        <ul>
            ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
        </ul>
    `;

    analysisContent.innerHTML = html;
    analysisContainer.scrollIntoView({ behavior: 'smooth' });
}

// Función para iniciar una nueva conversación
async function startConversation() {
    try {
        const response = await fetch('/api/start', {
            method: 'POST'
        });
        
        if (response.ok) {
            const message = await response.text();
            await addMessage(message);
            setInputEnabled(true);
            loadHistory();
        } else {
            console.error('Error al iniciar la conversación');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Función para enviar un mensaje
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message || isWaitingForResponse) return;

    isWaitingForResponse = true;
    await addMessage(message, true);
    userInput.value = '';
    setInputEnabled(false);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        if (response.ok) {
            const data = await response.json();
            
            if (data.analysis) {
                await addMessage(data.message);
                showAnalysis(data.analysis);
                isAnalysisComplete = true;
                await loadHistory();
            } else {
                await addMessage(data.message);
                setInputEnabled(true);
            }
        } else {
            console.error('Error en la respuesta del servidor');
            setInputEnabled(true);
        }
    } catch (error) {
        console.error('Error:', error);
        setInputEnabled(true);
    } finally {
        isWaitingForResponse = false;
    }
}

// Función para cargar el historial
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        if (response.ok) {
            const conversations = await response.json();
            displayConversationHistory(conversations);
        }
    } catch (error) {
        console.error('Error al cargar el historial:', error);
    }
}

// Función para mostrar el historial
function displayConversationHistory(conversations) {
    conversationHistory.innerHTML = '';
    conversations.forEach(conv => {
        const date = new Date(conv.timestamp);
        const convDiv = document.createElement('div');
        convDiv.className = 'conversation-item';
        convDiv.innerHTML = `
            <div class="conversation-date">
                ${date.toLocaleDateString()} ${date.toLocaleTimeString()}
            </div>
            <div class="conversation-id">ID: ${conv.id.slice(0, 8)}...</div>
        `;
        convDiv.onclick = () => loadConversation(conv.id);
        conversationHistory.appendChild(convDiv);
    });
}

// Función para cargar una conversación específica
async function loadConversation(conversationId) {
    try {
        const response = await fetch(`/api/conversation/${conversationId}`);
        if (response.ok) {
            const data = await response.json();
            displayLoadedConversation(data);
        }
    } catch (error) {
        console.error('Error al cargar la conversación:', error);
    }
}

// Función para mostrar una conversación cargada
function displayLoadedConversation(data) {
    chatMessages.innerHTML = '';
    analysisContainer.style.display = 'none';
    analysisContent.innerHTML = '';
    
    // Recrear el indicador de escritura después de limpiar el chat
    createTypingIndicator();
    
    if (data.messages) {
        data.messages.forEach(msg => {
            addMessage(msg.content, msg.role === 'USER');
        });
    }
    
    if (data.analysis) {
        showAnalysis(data.analysis);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', startConversation);

sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}); 