"""
Module containing prompt templates and questions for mental health triage.
"""
from typing import List, Dict

# Prompt base con contexto médico
BASE_CONTEXT = """
Eres un asistente especializado en triage inicial de salud mental. Tu rol es ayudar a realizar una evaluación 
preliminar para determinar la urgencia y posibles áreas de atención que requiere la persona.

Directrices importantes:
1. Mantén un tono profesional pero empático
2. No realices diagnósticos definitivos, solo sugerencias preliminares
3. Ante cualquier señal de riesgo inmediato, prioriza la seguridad del usuario
4. Sé directo y claro en tus preguntas
5. No des consejos terapéuticos, solo recomendaciones de búsqueda de ayuda profesional

Contexto: Estás realizando un triage inicial para evaluar la situación del usuario y determinar la urgencia 
de atención profesional requerida.
"""

# Lista de preguntas diagnósticas principales
DIAGNOSTIC_QUESTIONS = [
    {
        "id": "main_concern",
        "question": "¿Cuál es el principal motivo por el que buscas ayuda en este momento?",
        "purpose": "Identificar la preocupación principal y nivel de malestar"
    },
    {
        "id": "symptoms_duration",
        "question": "¿Desde hace cuánto tiempo te sientes así?",
        "purpose": "Evaluar la cronicidad de los síntomas"
    },
    {
        "id": "daily_impact",
        "question": "¿Cómo está afectando esta situación tu vida diaria (trabajo, relaciones, actividades)?",
        "purpose": "Evaluar el impacto funcional"
    },
    {
        "id": "mood_changes",
        "question": "¿Has notado cambios significativos en tu estado de ánimo recientemente?",
        "purpose": "Identificar alteraciones del estado de ánimo"
    },
    {
        "id": "sleep_patterns",
        "question": "¿Cómo han estado tus patrones de sueño últimamente?",
        "purpose": "Evaluar alteraciones del sueño"
    },
    {
        "id": "support_system",
        "question": "¿Cuentas con personas cercanas que te apoyen en este momento?",
        "purpose": "Evaluar red de apoyo social"
    },
    {
        "id": "previous_treatment",
        "question": "¿Has recibido ayuda profesional en salud mental anteriormente?",
        "purpose": "Identificar historial de tratamiento"
    },
    {
        "id": "self_harm",
        "question": "¿Has tenido pensamientos de hacerte daño o de que la vida no vale la pena?",
        "purpose": "Evaluar riesgo de autolesión",
        "priority": "high"
    },
    {
        "id": "substance_use",
        "question": "¿Has notado cambios en tu consumo de alcohol u otras sustancias?",
        "purpose": "Evaluar uso de sustancias"
    },
    {
        "id": "coping_mechanisms",
        "question": "¿Qué haces habitualmente cuando te sientes así?",
        "purpose": "Identificar estrategias de afrontamiento"
    }
]

# Template para el análisis final
ANALYSIS_TEMPLATE = """
Basado en las respuestas proporcionadas, realiza un análisis considerando:

1. Nivel de urgencia:
   - ALTO: Riesgo inmediato de autolesión o crisis aguda
   - MEDIO: Malestar significativo pero sin riesgo inmediato
   - BAJO: Malestar manejable, puede esperar atención regular

2. Áreas principales de preocupación (máximo 3)

3. Recomendaciones inmediatas:
   - Si es urgente: contacto inmediato con servicios de emergencia
   - Si es medio: consulta profesional en los próximos días
   - Si es bajo: consulta profesional para evaluación regular

Formato de respuesta requerido:
{
    "urgency_level": "ALTO|MEDIO|BAJO",
    "main_concerns": ["concern1", "concern2", "concern3"],
    "recommendations": ["rec1", "rec2", "rec3"],
    "risk_factors": ["risk1", "risk2"],
    "protective_factors": ["protective1", "protective2"]
}
"""

def format_question(question_id: str) -> Dict:
    """
    Obtiene una pregunta específica del conjunto de preguntas diagnósticas.
    
    Args:
        question_id (str): Identificador de la pregunta
    
    Returns:
        Dict: Pregunta formateada con su propósito y prioridad
    """
    for question in DIAGNOSTIC_QUESTIONS:
        if question["id"] == question_id:
            return question
    raise ValueError(f"Pregunta con ID {question_id} no encontrada")

def get_next_question(previous_responses: Dict[str, str]) -> Dict:
    """
    Determina la siguiente pregunta basada en las respuestas anteriores.
    
    Args:
        previous_responses (Dict[str, str]): Respuestas previas del usuario
    
    Returns:
        Dict: Siguiente pregunta a realizar
    """
    # Si hay indicios de riesgo alto en las respuestas previas,
    # priorizar preguntas de seguridad si aún no se han hecho
    if ("self_harm" not in previous_responses and
        any(risk_word in str(previous_responses.values()).lower() 
            for risk_word in ["suicid", "morir", "muerte", "daño", "crisis"])):
        return format_question("self_harm")
    
    # Obtener la siguiente pregunta que no ha sido respondida
    for question in DIAGNOSTIC_QUESTIONS:
        if question["id"] not in previous_responses:
            return question
            
    return None  # Todas las preguntas han sido respondidas

def format_analysis_prompt(responses: Dict[str, str]) -> str:
    """
    Formatea las respuestas para el análisis final.
    
    Args:
        responses (Dict[str, str]): Todas las respuestas del usuario
    
    Returns:
        str: Prompt formateado para el análisis final
    """
    responses_text = "\n".join([
        f"Pregunta: {format_question(q_id)['question']}\nRespuesta: {response}"
        for q_id, response in responses.items()
    ])
    
    return f"{BASE_CONTEXT}\n\nRespuestas del usuario:\n{responses_text}\n\n{ANALYSIS_TEMPLATE}" 