"""
Module for handling prompts and response analysis templates.
"""
from typing import Dict, List, Optional, Tuple

# Definición de categorías de síntomas y sus pesos
SYMPTOM_WEIGHTS = {
    "mood": {
        "depressed": 3,
        "anxious": 2,
        "irritable": 2,
        "hopeless": 3,
        "empty": 2
    },
    "behavior": {
        "isolation": 2,
        "avoidance": 2,
        "aggression": 3,
        "self_harm": 4,
        "substance_use": 3
    },
    "physical": {
        "sleep": 2,
        "appetite": 2,
        "energy": 2,
        "concentration": 2
    },
    "social": {
        "work_impact": 2,
        "relationship_impact": 2,
        "support_system": -1  # Factor protector
    }
}

# Criterios para niveles de urgencia
URGENCY_CRITERIA = {
    "ALTO": {
        "required": ["self_harm", "suicidal_ideation"],
        "threshold": 15
    },
    "MEDIO": {
        "threshold": 10
    },
    "BAJO": {
        "threshold": 0
    }
}

# Mapeo de diagnósticos preliminares
DIAGNOSTIC_CRITERIA = {
    "Depresión Mayor": {
        "required_symptoms": ["depressed_mood", "persistent_symptoms"],
        "additional_symptoms": [
            "sleep_changes",
            "energy_loss",
            "concentration_problems",
            "hopelessness",
            "loss_of_interest",
            "work_impact"
        ],
        "minimum_duration": 14,  # días
        "minimum_symptoms": 3
    },
    "Trastorno de Ansiedad Generalizada": {
        "required_symptoms": ["excessive_worry"],
        "additional_symptoms": [
            "restlessness",
            "fatigue",
            "concentration_problems",
            "sleep_changes"
        ],
        "minimum_duration": 180,  # días
        "minimum_symptoms": 3
    },
    "Trastorno de Pánico": {
        "required_symptoms": ["panic_attacks"],
        "additional_symptoms": [
            "fear",
            "heart_racing",
            "sweating",
            "trembling"
        ],
        "minimum_symptoms": 2
    }
}

# Temas requeridos para una evaluación completa
REQUIRED_TOPICS = [
    "main_concern",    # Motivo principal de consulta
    "duration",        # Duración de los síntomas
    "daily_impact",    # Impacto en la vida diaria
    "mood_changes",    # Cambios en el estado de ánimo
    "sleep",          # Patrones de sueño
    "support",        # Red de apoyo
    "previous_help",  # Ayuda profesional previa
    "self_harm",      # Pensamientos de autolesión
    "substance_use",  # Uso de sustancias
    "coping_mechanisms"  # Mecanismos de afrontamiento
]

def format_analysis_prompt(responses: Dict[str, str]) -> str:
    """
    Genera el prompt final para el análisis de las respuestas.
    
    Args:
        responses (Dict[str, str]): Diccionario de respuestas del usuario
    
    Returns:
        str: Prompt formateado para el análisis
    """
    # Contexto base para el análisis
    base_context = """Eres un asistente especializado en triage de salud mental. Tu tarea es analizar las respuestas 
    del paciente y proporcionar una evaluación preliminar estructurada. Sé empatico y considera cuidadosamente cada respuesta y 
    su contexto para identificar:

    1. Nivel de urgencia
    2. Principales preocupaciones
    3. Posibles diagnósticos preliminares
    4. Factores de riesgo
    5. Factores protectores
    6. Recomendaciones específicas

    Basándote en la siguiente información:"""

    # Formatear las respuestas para el análisis
    formatted_responses = "\n\nRespuestas del paciente:\n"
    for question_id, response in responses.items():
        formatted_responses += f"\n{question_id}: {response}"

    # Instrucciones para el análisis estructurado
    analysis_instructions = """
    
    Proporciona tu análisis en el siguiente formato JSON:
    {
        "urgency_level": "BAJO|MEDIO|ALTO",
        "main_concerns": ["lista", "de", "preocupaciones"],
        "preliminary_diagnoses": [
            {
                "condition": "nombre del trastorno",
                "confidence": "porcentaje de confianza",
                "key_indicators": ["lista", "de", "indicadores"]
            }
        ],
        "risk_factors": ["lista", "de", "factores"],
        "protective_factors": ["lista", "de", "factores"],
        "recommendations": ["lista", "de", "recomendaciones"]
    }

    Asegúrate de:
    1. Priorizar la seguridad del paciente
    2. Identificar señales de alarma
    3. Considerar el contexto completo
    4. Proporcionar recomendaciones específicas y accionables
    5. Mantener un enfoque conservador en los diagnósticos preliminares"""

    return base_context + formatted_responses + analysis_instructions

def validate_diagnosis(symptoms: List[str], criteria: Dict) -> bool:
    """
    Valida si un conjunto de síntomas cumple con los criterios diagnósticos.
    
    Args:
        symptoms (List[str]): Lista de síntomas identificados
        criteria (Dict): Criterios diagnósticos a validar
    
    Returns:
        bool: True si cumple los criterios, False en caso contrario
    """
    # Verificar síntomas requeridos
    required = criteria.get("required_symptoms", [])
    if not all(symptom in symptoms for symptom in required):
        return False
    
    # Verificar cantidad mínima de síntomas adicionales
    additional = criteria.get("additional_symptoms", [])
    additional_count = sum(1 for symptom in symptoms if symptom in additional)
    
    if "minimum_symptoms" in criteria:
        total_symptoms = len([s for s in symptoms if s in required + additional])
        if total_symptoms < criteria["minimum_symptoms"]:
            return False
    
    return True

def calculate_urgency_level(symptoms: List[str], weights: Dict) -> str:
    """
    Calcula el nivel de urgencia basado en los síntomas y sus pesos.
    
    Args:
        symptoms (List[str]): Lista de síntomas identificados
        weights (Dict): Pesos de los síntomas
    
    Returns:
        str: Nivel de urgencia (BAJO, MEDIO, ALTO)
    """
    total_weight = 0
    
    # Calcular peso total
    for symptom in symptoms:
        for category in weights.values():
            if symptom in category:
                total_weight += category[symptom]
    
    # Verificar criterios de urgencia alta
    if any(symptom in URGENCY_CRITERIA["ALTO"]["required"] for symptom in symptoms):
        return "ALTO"
    
    # Determinar nivel por umbral
    if total_weight >= URGENCY_CRITERIA["MEDIO"]["threshold"]:
        return "MEDIO"
    
    return "BAJO"

def get_next_question(previous_responses: Dict[str, str]) -> Optional[str]:
    """
    Determina la siguiente pregunta basada en las respuestas previas.
    
    Args:
        previous_responses (Dict[str, str]): Diccionario de respuestas previas
    
    Returns:
        Optional[str]: ID de la siguiente pregunta o None si no hay más preguntas
    """
    # Lista de preguntas en orden
    question_sequence = [
        "main_concern",
        "duration",
        "daily_impact",
        "mood_changes",
        "sleep",
        "support",
        "previous_help",
        "self_harm",
        "substance_use",
        "coping_mechanisms"
    ]
    
    # Si no hay respuestas previas, comenzar con la primera pregunta
    if not previous_responses:
        return question_sequence[0]
    
    # Obtener todas las preguntas ya realizadas
    asked_questions = set(previous_responses.keys())
    
    # Priorizar preguntas de seguridad si aún no se han hecho y hay indicadores de riesgo
    if ("self_harm" not in asked_questions and
        any(risk_word in str(previous_responses.values()).lower() 
            for risk_word in ["suicid", "morir", "muerte", "daño", "crisis"])):
        return "self_harm"
    
    # Encontrar la siguiente pregunta en la secuencia
    for question in question_sequence:
        if question not in asked_questions:
            return question
    
    # Si todas las preguntas han sido respondidas
    return None

def get_conversation_prompt(
    current_message: str,
    chat_history: List[Tuple[str, str]],
    covered_topics: Dict[str, bool],
    collected_responses: Dict[str, str]
) -> str:
    """
    Genera un prompt para el LLM que incluye el contexto de la conversación.
    
    Args:
        current_message (str): Mensaje actual del usuario
        chat_history (List[Tuple[str, str]]): Historial de la conversación
        covered_topics (Dict[str, bool]): Temas cubiertos hasta el momento
        collected_responses (Dict[str, str]): Respuestas recolectadas
    
    Returns:
        str: Prompt para el LLM
    """
    # Contexto base
    prompt = """Eres un asistente especializado en salud mental, realizando una evaluación inicial.
Tu objetivo es mantener una conversación natural y empática mientras recopilas información importante.

CONTEXTO DE LA CONVERSACIÓN:
"""
    
    # Agregar historial de la conversación
    prompt += "\nHistorial de la conversación:\n"
    for role, message in chat_history[-5:]:  # Últimos 5 mensajes para contexto
        prompt += f"{role}: {message}\n"
    
    # Agregar temas pendientes
    pending_topics = [topic for topic, covered in covered_topics.items() if not covered]
    prompt += "\nTemas pendientes de explorar:\n"
    for topic in pending_topics:
        prompt += f"- {topic}\n"
    
    # Instrucciones específicas
    prompt += """
INSTRUCCIONES:
1. Mantén un tono empático y conversacional
2. Prioriza temas de riesgo si se detectan señales
3. Haz preguntas naturales de seguimiento basadas en las respuestas
4. Evita cambios bruscos de tema
5. Asegúrate de cubrir todos los temas pendientes de manera orgánica
6. Si detectas señales de riesgo, profundiza inmediatamente

SEÑALES DE RIESGO A VIGILAR:
- Pensamientos de autolesión o suicidio
- Pérdida severa de funcionalidad
- Síntomas psicóticos
- Consumo problemático de sustancias

Por favor, genera una respuesta natural y empática que ayude a explorar los temas pendientes,
manteniendo el flujo de la conversación y respondiendo apropiadamente al último mensaje del usuario."""

    return prompt 