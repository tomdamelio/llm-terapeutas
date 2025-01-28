"""
Module for integrating with Google's Gemini LLM API.
"""
import time
import json
from typing import Dict, Optional
import google.generativeai as genai
import config

def initialize_llm() -> None:
    """
    Initialize the Gemini LLM with API configuration.
    """
    try:
        genai.configure(api_key=config.GOOGLE_API_KEY)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Gemini LLM: {str(e)}")

def send_prompt(prompt: str, max_retries: int = 3, retry_delay: float = 1.0) -> str:
    """
    Send a prompt to the Gemini LLM and get the response.
    
    Args:
        prompt (str): The input prompt to send to the model
        max_retries (int): Maximum number of retry attempts
        retry_delay (float): Delay between retries in seconds
    
    Returns:
        str: The model's response text
    
    Raises:
        RuntimeError: If all retry attempts fail
    """
    model = genai.GenerativeModel('gemini-pro')
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                raise RuntimeError(f"Failed to get response after {max_retries} attempts: {str(e)}")
            time.sleep(retry_delay)

def process_response(response: str) -> Dict[str, any]:
    """
    Process the raw response from the LLM into a structured format.
    
    Args:
        response (str): Raw response from the LLM
    
    Returns:
        Dict[str, any]: Structured response containing:
            - urgency_level (str): ALTO, MEDIO, o BAJO
            - main_concerns (list): Lista de preocupaciones principales
            - recommendations (list): Lista de recomendaciones
            - risk_factors (list): Factores de riesgo identificados
            - protective_factors (list): Factores protectores identificados
    """
    try:
        # Buscar el JSON en la respuesta
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No se encontró formato JSON en la respuesta")
            
        json_str = response[start_idx:end_idx]
        data = json.loads(json_str)
        
        # Validar campos requeridos
        required_fields = ['urgency_level', 'main_concerns', 'recommendations']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Campo requerido '{field}' no encontrado en la respuesta")
        
        # Asegurar que los campos opcionales existan
        data.setdefault('risk_factors', [])
        data.setdefault('protective_factors', [])
        
        return data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al decodificar JSON de la respuesta: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error al procesar respuesta del LLM: {str(e)}")

def get_model_info() -> Optional[Dict[str, any]]:
    """
    Get information about the available models and their configurations.
    
    Returns:
        Optional[Dict[str, any]]: Information about the models or None if unavailable
    """
    try:
        models = genai.list_models()
        return {model.name: model.supported_generation_methods for model in models}
    except Exception as e:
        print(f"Warning: Failed to get model information: {str(e)}")
        return None 