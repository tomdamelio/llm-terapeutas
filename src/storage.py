"""
Module for handling conversation storage and retrieval.
"""
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Optional

# Definir la estructura del directorio de datos
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
CONVERSATIONS_DIR = os.path.join(DATA_DIR, 'conversations')

# Asegurar que los directorios existan
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

def generate_conversation_id() -> str:
    """
    Genera un ID único para la conversación.
    
    Returns:
        str: ID único en formato UUID
    """
    return str(uuid.uuid4())

def create_conversation_structure(
    responses: Dict[str, str],
    analysis: Optional[Dict] = None
) -> Dict:
    """
    Crea la estructura JSON para almacenar la conversación.
    
    Args:
        responses (Dict[str, str]): Respuestas del usuario
        analysis (Optional[Dict]): Resultado del análisis del LLM
    
    Returns:
        Dict: Estructura completa de la conversación
    """
    return {
        "metadata": {
            "conversation_id": generate_conversation_id(),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        },
        "conversation": {
            "responses": responses,
            "analysis": analysis or {}
        }
    }

def save_conversation(conversation_data: Dict) -> str:
    """
    Guarda una conversación en el sistema de archivos.
    
    Args:
        conversation_data (Dict): Datos de la conversación y análisis
    
    Returns:
        str: ID de la conversación guardada
    
    Raises:
        IOError: Si hay un error al escribir el archivo
    """
    try:
        # Crear estructura si no existe
        if "metadata" not in conversation_data:
            conversation_data = create_conversation_structure(
                conversation_data.get("responses", {}),
                conversation_data.get("analysis")
            )
        
        conversation_id = conversation_data["metadata"]["conversation_id"]
        filename = f"{conversation_id}.json"
        filepath = os.path.join(CONVERSATIONS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
        return conversation_id
        
    except Exception as e:
        raise IOError(f"Error al guardar la conversación: {str(e)}")

def load_conversation(conversation_id: str) -> Optional[Dict]:
    """
    Carga una conversación desde el sistema de archivos.
    
    Args:
        conversation_id (str): ID de la conversación a cargar
    
    Returns:
        Optional[Dict]: Datos de la conversación o None si no se encuentra
    
    Raises:
        IOError: Si hay un error al leer el archivo
    """
    try:
        filename = f"{conversation_id}.json"
        filepath = os.path.join(CONVERSATIONS_DIR, filename)
        
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        raise IOError(f"Error al cargar la conversación: {str(e)}")

def list_conversations(limit: int = 10) -> list:
    """
    Lista las conversaciones más recientes.
    
    Args:
        limit (int): Número máximo de conversaciones a retornar
    
    Returns:
        list: Lista de metadatos de conversaciones
    """
    try:
        conversations = []
        for filename in os.listdir(CONVERSATIONS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CONVERSATIONS_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversations.append(data["metadata"])
        
        # Ordenar por timestamp descendente y limitar
        conversations.sort(
            key=lambda x: x["timestamp"],
            reverse=True
        )
        return conversations[:limit]
        
    except Exception as e:
        print(f"Error al listar conversaciones: {str(e)}")
        return [] 