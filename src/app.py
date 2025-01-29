"""
Aplicación Flask para el sistema de triage en salud mental.
"""
from flask import Flask, request, jsonify, render_template, url_for
from datetime import datetime
import json
import logging

from chatbot import ChatBot
import storage

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
chatbot = ChatBot()

@app.route('/')
def index():
    """Ruta principal que muestra la página de inicio."""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Ruta que muestra la interfaz del chat."""
    return render_template('chat.html')

@app.route('/history')
def history():
    """Ruta que muestra el historial de conversaciones."""
    return render_template('history.html')

@app.route('/api/start', methods=['POST'])
def start_conversation():
    """Inicia una nueva conversación."""
    try:
        initial_message = chatbot.start_conversation()
        return jsonify({
            "message": initial_message,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error al iniciar conversación: {str(e)}")
        return jsonify({
            "error": "Error al iniciar la conversación",
            "status": "error"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_message():
    """Procesa los mensajes del chat."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "error": "Mensaje no proporcionado",
                "status": "error"
            }), 400

        response = chatbot.process_message(data['message'])
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error al procesar mensaje: {str(e)}")
        return jsonify({
            "error": "Error al procesar el mensaje",
            "status": "error"
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Obtiene el historial de conversaciones."""
    try:
        conversations = storage.get_conversation_history()
        formatted_conversations = []
        
        for conv in conversations:
            formatted_conv = {
                "id": conv["metadata"]["conversation_id"],
                "date": conv["metadata"]["timestamp"],
                "main_concern": conv["conversation"]["responses"].get("main_concern", ""),
                "urgency_level": conv["conversation"]["analysis"].get("urgency_level", "BAJO") if conv["conversation"].get("analysis") else "BAJO"
            }
            formatted_conversations.append(formatted_conv)
        
        return jsonify({
            "conversations": formatted_conversations,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error al obtener historial: {str(e)}")
        return jsonify({
            "error": "Error al obtener el historial",
            "status": "error"
        }), 500

@app.route('/api/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Obtiene una conversación específica por ID."""
    try:
        conversation = storage.load_conversation(conversation_id)
        if conversation:
            # Formatear la conversación para la UI
            formatted_conversation = {
                "metadata": conversation["metadata"],
                "responses": conversation["conversation"]["responses"],
                "analysis": conversation["conversation"]["analysis"] if "analysis" in conversation["conversation"] else None
            }
            return jsonify({
                "conversation": formatted_conversation,
                "status": "success"
            })
        else:
            return jsonify({
                "error": "Conversación no encontrada",
                "status": "error"
            }), 404
    except Exception as e:
        logger.error(f"Error al obtener conversación {conversation_id}: {str(e)}")
        return jsonify({
            "error": "Error al obtener la conversación",
            "status": "error"
        }), 500

@app.route('/api/report/<conversation_id>', methods=['GET'])
def generate_report(conversation_id):
    """Genera un reporte PDF de la conversación."""
    try:
        conversation = storage.load_conversation(conversation_id)
        if not conversation:
            return jsonify({
                "error": "Conversación no encontrada",
                "status": "error"
            }), 404

        # Aquí iría la lógica para generar el PDF
        # Por ahora retornamos los datos en JSON
        return jsonify({
            "report": conversation,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error al generar reporte para {conversation_id}: {str(e)}")
        return jsonify({
            "error": "Error al generar el reporte",
            "status": "error"
        }), 500

@app.errorhandler(404)
def not_found_error(error):
    """Maneja errores 404."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Maneja errores 500."""
    logger.error(f"Error interno del servidor: {str(error)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True) 