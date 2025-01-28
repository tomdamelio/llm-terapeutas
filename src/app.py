"""
Flask application for the Mental Health Triage Chatbot.
"""
from flask import Flask, request, jsonify, render_template
from chatbot import ChatBot
import storage

app = Flask(__name__)
chatbot = ChatBot()

@app.route('/')
def home():
    """Render the chat interface."""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_conversation():
    """Start a new conversation."""
    try:
        initial_message = chatbot.start_conversation()
        return initial_message
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process a message and return the chatbot's response."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
        
        response = chatbot.process_message(data['message'])
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history')
def get_history():
    """Get the conversation history."""
    try:
        conversations = storage.get_conversation_history()
        formatted_conversations = []
        for conv in conversations:
            formatted_conversations.append({
                'id': conv['metadata']['conversation_id'],
                'timestamp': conv['metadata']['timestamp']
            })
        return jsonify(formatted_conversations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversation/<conversation_id>')
def get_conversation(conversation_id):
    """Get a specific conversation by ID."""
    try:
        conversation = storage.load_conversation(conversation_id)
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
        
        # Formatear los mensajes para la visualización
        messages = []
        for question_id, response in conversation['conversation']['responses'].items():
            if question_id in chatbot.QUESTION_MAP:
                messages.append({
                    'role': 'ASSISTANT',
                    'content': chatbot.QUESTION_MAP[question_id]
                })
                messages.append({
                    'role': 'USER',
                    'content': response
                })
        
        return jsonify({
            'messages': messages,
            'analysis': conversation['conversation'].get('analysis')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 