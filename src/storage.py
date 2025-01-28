"""
Module for handling conversation storage and retrieval.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# Definir la estructura del directorio de datos
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
CONVERSATIONS_DIR = os.path.join(DATA_DIR, 'conversations')

# Asegurar que los directorios existan
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

def get_conversation_history() -> List[Dict]:
    """
    Obtiene el historial de conversaciones.
    
    Returns:
        List[Dict]: Lista de conversaciones ordenadas por fecha
    """
    conversations = []
    try:
        for filename in os.listdir(CONVERSATIONS_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(CONVERSATIONS_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversation = json.load(f)
                    conversations.append(conversation)
        
        # Ordenar por fecha, más reciente primero
        conversations.sort(key=lambda x: x['metadata']['timestamp'], reverse=True)
        return conversations
    except Exception as e:
        print(f"Error al cargar el historial: {str(e)}")
        return []

def save_conversation(conversation_data: Dict) -> str:
    """
    Guarda una conversación en el sistema de archivos.
    
    Args:
        conversation_data (Dict): Datos de la conversación
    
    Returns:
        str: ID de la conversación guardada
    """
    try:
        conversation_id = conversation_data['metadata']['conversation_id']
        file_path = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)
        
        return conversation_id
    except Exception as e:
        print(f"Error al guardar la conversación: {str(e)}")
        return None

def load_conversation(conversation_id: str) -> Optional[Dict]:
    """
    Carga una conversación específica.
    
    Args:
        conversation_id (str): ID de la conversación a cargar
    
    Returns:
        Optional[Dict]: Datos de la conversación o None si no se encuentra
    """
    try:
        file_path = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error al cargar la conversación: {str(e)}")
        return None 