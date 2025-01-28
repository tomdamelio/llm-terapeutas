"""
Aplicación web Flask para el chatbot de triage en salud mental.
"""
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session
)
from chatbot import ChatBot
import storage

app = Flask(__name__)
# Configurar una clave secreta para las sesiones
app.secret_key = 'tu_clave_secreta_aqui'  # En producción, usar una clave segura

@app.route('/')
def home():
    """Página principal con el chat."""
    return render_template('chat.html')

@app.route('/api/start', methods=['POST'])
def start_conversation():
    """Inicia una nueva conversación."""
    try:
        bot = ChatBot()
        bot.start_conversation()
        
        # Obtener la primera pregunta
        next_question = bot.get_next_question({})
        
        # Guardar el estado en la sesión
        session['responses'] = {}
        
        return jsonify({
            'status': 'success',
            'question': next_question['question'],
            'question_id': next_question['id']
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Procesa la respuesta del usuario y devuelve la siguiente pregunta."""
    try:
        data = request.json
        response = data.get('response', '').strip()
        question_id = data.get('question_id')
        
        if not response or not question_id:
            return jsonify({
                'status': 'error',
                'message': 'Respuesta o ID de pregunta faltante'
            }), 400
        
        # Recuperar respuestas anteriores de la sesión
        responses = session.get('responses', {})
        responses[question_id] = response
        session['responses'] = responses
        
        # Obtener siguiente pregunta
        bot = ChatBot()
        next_question = bot.get_next_question(responses)
        
        # Si no hay más preguntas, realizar análisis
        if not next_question:
            bot.responses = responses
            analysis = bot.run_conversation()
            
            if analysis:
                return jsonify({
                    'status': 'success',
                    'finished': True,
                    'analysis': analysis,
                    'conversation_id': bot.conversation_id
                })
        
        return jsonify({
            'status': 'success',
            'finished': False,
            'question': next_question['question'],
            'question_id': next_question['id']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Obtiene el historial de conversaciones."""
    try:
        conversations = storage.list_conversations(limit=10)
        return jsonify({
            'status': 'success',
            'conversations': conversations
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Obtiene los detalles de una conversación específica."""
    try:
        bot = ChatBot()
        if bot.load_conversation(conversation_id):
            return jsonify({
                'status': 'success',
                'conversation': {
                    'responses': bot.responses,
                    'analysis': bot.analysis
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Conversación no encontrada'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 