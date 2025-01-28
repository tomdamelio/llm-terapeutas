"""
Module for the ChatBot implementation that handles the conversation flow.
"""
from typing import Dict, Optional, List, Tuple
import json
from datetime import datetime

from prompts import (
    get_conversation_prompt,
    format_analysis_prompt,
    calculate_urgency_level,
    validate_diagnosis,
    SYMPTOM_WEIGHTS,
    DIAGNOSTIC_CRITERIA,
    REQUIRED_TOPICS
)
from diagnosis_parser import (
    parse_llm_response,
    format_json_response,
    format_diagnosis,
    AnalysisResult
)
import storage

# Mapeo de IDs de preguntas a sus textos
QUESTION_MAP = {
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
}

class ChatBot:
    """
    Clase que maneja la conversación con el usuario y la interacción con el LLM.
    """
    
    def __init__(self):
        """Inicializa el chatbot."""
        self.responses: Dict[str, str] = {}
        self.conversation_active = False
        self.conversation_id: Optional[str] = None
        self.analysis: Optional[AnalysisResult] = None
        self.chat_history: List[Tuple[str, str]] = []  # [(user_message, bot_response), ...]
        self.covered_topics: Dict[str, bool] = {topic: False for topic in REQUIRED_TOPICS}
    
    def start_conversation(self) -> str:
        """
        Inicia una nueva conversación.
        
        Returns:
            str: Mensaje inicial del chatbot
        """
        self.responses = {}
        self.conversation_active = True
        self.conversation_id = None
        self.analysis = None
        self.chat_history = []
        self.covered_topics = {topic: False for topic in REQUIRED_TOPICS}
        
        initial_message = ("Hola, soy un asistente especializado en salud mental. "
                         "Estoy aquí para escucharte y ayudarte. ¿Podrías contarme "
                         "qué te trae por aquí hoy?")
        
        self.chat_history.append(("SYSTEM", initial_message))
        return initial_message
    
    def process_message(self, user_message: str) -> Dict:
        """
        Procesa el mensaje del usuario y genera una respuesta contextual.
        
        Args:
            user_message (str): Mensaje del usuario
        
        Returns:
            Dict: Respuesta del chatbot con mensaje y análisis opcional
        """
        if not self.conversation_active:
            return {"message": "La conversación no está activa. Por favor, inicia una nueva conversación."}
        
        # Guardar el mensaje del usuario en el historial
        self.chat_history.append(("USER", user_message))
        
        # Buscar la última pregunta del bot
        last_question = None
        last_question_id = None
        for i in range(len(self.chat_history) - 2, -1, -1):
            if self.chat_history[i][0] == "ASSISTANT":
                last_question = self.chat_history[i][1]
                # Encontrar el ID de la pregunta
                for q_id, q_text in QUESTION_MAP.items():
                    if q_text in last_question:
                        last_question_id = q_id
                        break
                break
        
        # Actualizar respuestas solo si encontramos la pregunta correspondiente
        if last_question_id and last_question_id not in self.responses:
            self.responses[last_question_id] = user_message
            self.covered_topics[last_question_id] = True
            
            # Si es una respuesta con señales de riesgo, marcar self_harm
            message_lower = user_message.lower()
            risk_keywords = ["suicid", "morir", "muerte", "daño", "crisis"]
            if any(keyword in message_lower for keyword in risk_keywords) and "self_harm" not in self.responses:
                self.responses["self_harm"] = user_message
                self.covered_topics["self_harm"] = True
        
        # Obtener la siguiente pregunta
        next_question_id = self._get_next_question()
        
        if next_question_id:
            # Verificar que no estamos repitiendo la última pregunta
            next_question = QUESTION_MAP[next_question_id]
            if last_question == next_question:
                # Si la pregunta se repetiría, buscar la siguiente
                for q_id in QUESTION_MAP:
                    if q_id not in self.responses and q_id != next_question_id:
                        next_question_id = q_id
                        next_question = QUESTION_MAP[q_id]
                        break
            
            # Si aún tenemos una pregunta válida, enviarla
            if next_question_id and next_question_id not in self.responses:
                self.chat_history.append(("ASSISTANT", next_question))
                return {"message": next_question}
            else:
                # Si no hay más preguntas, proceder con el análisis
                final_message = self._prepare_for_analysis()
                analysis = self._analyze_responses()
                self.chat_history.append(("ASSISTANT", final_message))
                return {
                    "message": final_message,
                    "analysis": analysis
                }
        else:
            # Si no hay más preguntas, proceder con el análisis
            final_message = self._prepare_for_analysis()
            analysis = self._analyze_responses()
            self.chat_history.append(("ASSISTANT", final_message))
            return {
                "message": final_message,
                "analysis": analysis
            }
    
    def _get_next_question(self) -> Optional[str]:
        """
        Determina la siguiente pregunta basada en las respuestas y temas cubiertos.
        
        Returns:
            Optional[str]: ID de la siguiente pregunta o None si no hay más
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
        
        # Si no hay respuestas, comenzar con la primera pregunta
        if not self.responses:
            return question_sequence[0]
        
        # Priorizar preguntas de seguridad si hay indicadores de riesgo y no se ha preguntado aún
        if ("self_harm" not in self.responses and
            any(risk_word in str(self.responses.values()).lower() 
                for risk_word in ["suicid", "morir", "muerte", "daño", "crisis"])):
            return "self_harm"
        
        # Encontrar la siguiente pregunta no respondida
        for question in question_sequence:
            if question not in self.responses:
                return question
        
        # Si todas las preguntas han sido respondidas
        return None
    
    def _generate_follow_up_question(self, user_message: str) -> str:
        """
        Genera una pregunta de seguimiento basada en el contexto.
        
        Args:
            user_message (str): Último mensaje del usuario
        
        Returns:
            str: Pregunta de seguimiento
        """
        # Analizar el mensaje para identificar temas mencionados
        message_lower = user_message.lower()
        
        # Verificar si hay señales de riesgo que requieran atención inmediata
        risk_keywords = ["suicid", "morir", "daño", "muerte"]
        if any(keyword in message_lower for keyword in risk_keywords) and not self.covered_topics["self_harm"]:
            self.covered_topics["self_harm"] = True
            return ("Me preocupa lo que me cuentas. ¿Podrías decirme más sobre estos pensamientos? "
                   "Es importante que sepas que hay ayuda disponible y personas que se preocupan por ti.")
        
        # Priorizar temas no cubiertos basados en el contexto
        if "mal" in message_lower and "dorm" in message_lower and not self.covered_topics["sleep"]:
            self.covered_topics["sleep"] = True
            return "¿Hace cuánto tiempo que tienes dificultades con el sueño? ¿Cómo afecta esto tu día a día?"
        
        if ("trabajo" in message_lower or "estudio" in message_lower) and not self.covered_topics["daily_impact"]:
            self.covered_topics["daily_impact"] = True
            return "¿Cómo está afectando esta situación tu desempeño en el trabajo/estudio? ¿Has notado cambios significativos?"
        
        # Si se mencionan emociones, indagar más
        emotion_keywords = ["triste", "ansios", "preocupa", "angustia", "miedo"]
        if any(keyword in message_lower for keyword in emotion_keywords) and not self.covered_topics["mood_changes"]:
            self.covered_topics["mood_changes"] = True
            return "¿Podrías contarme más sobre estos sentimientos? ¿Hace cuánto tiempo te sientes así?"
        
        # Buscar el primer tema no cubierto
        for topic, covered in self.covered_topics.items():
            if not covered:
                return self._get_natural_question_for_topic(topic)
        
        # Si todos los temas están cubiertos, proceder al análisis
        return self._prepare_for_analysis()
    
    def _get_natural_question_for_topic(self, topic: str) -> str:
        """
        Genera una pregunta natural para un tema específico.
        
        Args:
            topic (str): Tema a cubrir
        
        Returns:
            str: Pregunta formulada naturalmente
        """
        # Verificar si la pregunta ya está en el historial
        for _, message in self.chat_history:
            if message in QUESTION_MAP.values():
                # Si la pregunta ya se hizo, usar una variante
                if topic == "main_concern":
                    return "¿Podrías decirme más sobre lo que te preocupa?"
                elif topic == "duration":
                    return "¿Desde hace cuánto tiempo te ocurre esto?"
                elif topic == "daily_impact":
                    return "¿De qué manera está afectando tu vida diaria?"
                elif topic == "mood_changes":
                    return "¿Has percibido cambios en tu estado de ánimo?"
                elif topic == "sleep":
                    return "Cuéntame sobre tu sueño, ¿cómo has estado durmiendo?"
                elif topic == "support":
                    return "¿Cuentas con personas que te apoyen en este momento?"
                elif topic == "previous_help":
                    return "¿Has consultado con algún profesional anteriormente?"
                elif topic == "self_harm":
                    return "¿Has tenido pensamientos de hacerte daño?"
                elif topic == "substance_use":
                    return "¿Has notado cambios en el consumo de alcohol u otras sustancias?"
                elif topic == "coping_mechanisms":
                    return "¿Qué sueles hacer cuando te sientes así?"
        
        # Si la pregunta no se ha hecho antes, usar la versión estándar
        return QUESTION_MAP.get(topic, "¿Hay algo más que quieras contarme?")
    
    def _update_responses_and_topics(self, user_message: str) -> None:
        """
        Actualiza las respuestas y temas cubiertos basado en el mensaje del usuario.
        
        Args:
            user_message (str): Mensaje del usuario
        """
        # Identificar el tema más probable basado en el último intercambio
        last_bot_message = None
        for i in range(len(self.chat_history) - 2, -1, -1):
            if self.chat_history[i][0] == "ASSISTANT":
                last_bot_message = self.chat_history[i][1]
                break
        
        if not last_bot_message:
            return
            
        # Buscar a qué pregunta corresponde la respuesta
        for topic, question in QUESTION_MAP.items():
            if question in last_bot_message and topic not in self.responses:
                self.responses[topic] = user_message
                self.covered_topics[topic] = True
                break
    
    def _is_response_relevant_to_topic(self, question: str, answer: str, topic: str) -> bool:
        """
        Determina si una respuesta es relevante para un tema específico.
        
        Args:
            question (str): Pregunta del bot
            answer (str): Respuesta del usuario
            topic (str): Tema a evaluar
        
        Returns:
            bool: True si la respuesta es relevante para el tema
        """
        # Implementar lógica de relevancia basada en palabras clave y contexto
        topic_keywords = {
            "main_concern": ["preocupa", "problema", "motivo", "razón"],
            "duration": ["tiempo", "desde", "hace", "cuando"],
            "daily_impact": ["afecta", "impacto", "trabajo", "estudio", "relaciones"],
            "mood_changes": ["ánimo", "cambios", "sientes", "emociones"],
            "sleep": ["dormir", "sueño", "descanso", "insomnio"],
            "support": ["apoyo", "familia", "amigos", "cerca"],
            "previous_help": ["ayuda", "profesional", "terapeuta", "psicólogo"],
            "self_harm": ["daño", "morir", "suicid", "lastimar"],
            "substance_use": ["alcohol", "drogas", "sustancias", "consumo"],
            "coping_mechanisms": ["ayuda", "calma", "mejora", "alivio"]
        }
        
        keywords = topic_keywords.get(topic, [])
        return any(keyword in question.lower() or keyword in answer.lower() for keyword in keywords)
    
    def _prepare_for_analysis(self) -> str:
        """
        Prepara el cierre de la conversación y el análisis.
        
        Returns:
            str: Mensaje de cierre
        """
        return ("Gracias por compartir todo esto conmigo. Con la información que me has dado, "
                "puedo preparar un análisis de la situación y recomendaciones específicas. "
                "¿Hay algo más que quieras agregar antes de proceder con el análisis?")
    
    def _extract_symptoms(self, responses: Dict[str, str]) -> list:
        """
        Extrae síntomas de las respuestas del usuario.
        
        Args:
            responses (Dict[str, str]): Respuestas del usuario
        
        Returns:
            list: Lista de síntomas identificados
        """
        symptoms = []
        
        # Mapeo de palabras clave a síntomas
        keyword_mapping = {
            "triste": "depressed_mood",
            "deprimid": "depressed_mood",
            "sin esperanza": "hopelessness",
            "sin ganas": "loss_of_interest",
            "ansios": "excessive_worry",
            "preocupad": "excessive_worry",
            "dormir": "sleep_changes",
            "insomnio": "sleep_changes",
            "cansad": "fatigue",
            "sin energía": "energy_loss",
            "sol": "isolation",
            "aislad": "isolation",
            "miedo": "fear",
            "pánico": "panic_attacks",
            "daño": "self_harm",
            "morir": "suicidal_ideation",
            "suicid": "suicidal_ideation",
            "concentr": "concentration_problems",
            "trabajar": "work_impact",
            "relacion": "relationship_impact"
        }
        
        # Buscar palabras clave en las respuestas
        for response in responses.values():
            response_lower = response.lower()
            for keyword, symptom in keyword_mapping.items():
                if keyword in response_lower and symptom not in symptoms:
                    symptoms.append(symptom)
        
        # Análisis específico por tipo de pregunta
        if "duration" in responses:
            duration = responses["duration"].lower()
            if any(term in duration for term in ["semana", "mes"]):
                symptoms.append("persistent_symptoms")
        
        if "daily_impact" in responses and "trabajo" in responses["daily_impact"].lower():
            symptoms.append("work_impact")
            
        if "mood_changes" in responses and "sí" in responses["mood_changes"].lower():
            symptoms.append("mood_changes")
            
        if "sleep" in responses and any(term in responses["sleep"].lower() for term in ["mal", "poco", "mucho", "problema"]):
            symptoms.append("sleep_changes")
            
        if "support" in responses and all(term not in responses["support"].lower() for term in ["sí", "si", "familia", "amigo"]):
            symptoms.append("lack_of_support")
        
        return symptoms
    
    def _analyze_responses(self) -> Dict:
        """
        Analiza las respuestas para generar un diagnóstico preliminar.
        
        Returns:
            Dict: Análisis completo de las respuestas
        """
        # Extraer síntomas de las respuestas
        symptoms = self._extract_symptoms(self.responses)
        
        # Calcular nivel de urgencia
        urgency_level = calculate_urgency_level(symptoms, SYMPTOM_WEIGHTS)
        
        # Identificar posibles diagnósticos
        preliminary_diagnoses = []
        for condition, criteria in DIAGNOSTIC_CRITERIA.items():
            if validate_diagnosis(symptoms, criteria):
                # Calcular confianza basada en la cantidad de síntomas presentes
                required_symptoms = criteria.get("required_symptoms", [])
                additional_symptoms = criteria.get("additional_symptoms", [])
                total_possible = len(required_symptoms) + len(additional_symptoms)
                matched_symptoms = [s for s in symptoms if s in required_symptoms + additional_symptoms]
                confidence = len(matched_symptoms) / total_possible * 100
                
                preliminary_diagnoses.append({
                    "condition": condition,
                    "confidence": confidence,
                    "key_indicators": matched_symptoms
                })
        
        # Identificar factores de riesgo
        risk_factors = []
        if "self_harm" in symptoms or "suicidal_ideation" in symptoms:
            risk_factors.append("Riesgo de autolesión o ideación suicida")
        if "substance_use" in symptoms:
            risk_factors.append("Uso problemático de sustancias")
        if "isolation" in symptoms:
            risk_factors.append("Aislamiento social significativo")
        
        # Identificar factores protectores
        protective_factors = []
        if "support" in self.responses:
            response = self.responses["support"].lower()
            if "sí" in response or "si" in response or "familia" in response or "amigos" in response:
                protective_factors.append("Red de apoyo social disponible")
        
        # Generar recomendaciones
        recommendations = []
        if urgency_level == "ALTO":
            recommendations.append("Buscar ayuda profesional inmediata - contactar servicios de emergencia")
            recommendations.append("No permanecer solo/a - contactar a un familiar o amigo de confianza")
        elif urgency_level == "MEDIO":
            recommendations.append("Programar consulta profesional en los próximos días")
            recommendations.append("Mantener contacto regular con red de apoyo")
        else:
            recommendations.append("Programar una evaluación profesional cuando sea conveniente")
            recommendations.append("Mantener registro de síntomas y su frecuencia")
        
        # Crear el análisis en formato JSON
        analysis_json = {
            "urgency_level": urgency_level,
            "main_concerns": [s.replace("_", " ").title() for s in symptoms[:3]],
            "preliminary_diagnoses": preliminary_diagnoses,
            "risk_factors": risk_factors,
            "protective_factors": protective_factors,
            "recommendations": recommendations
        }
        
        # Parsear y validar el análisis
        self.analysis = parse_llm_response(json.dumps(analysis_json))
        if not self.analysis:
            raise ValueError("Error al parsear el análisis")
        
        # Retornar el análisis en formato JSON para la API
        return format_json_response(self.analysis)
    
    def run_conversation(self) -> Optional[Dict]:
        """
        Ejecuta el análisis final de la conversación.
        
        Returns:
            Optional[Dict]: Resultados del análisis o None si hay un error
        """
        try:
            # Generar análisis basado en las respuestas actuales
            analysis_json = self._analyze_responses()
            
            # Guardar la conversación
            conversation_data = storage.create_conversation_structure(
                self.responses,
                analysis_json
            )
            self.conversation_id = conversation_data["metadata"]["conversation_id"]
            storage.save_conversation(conversation_data)
            
            return analysis_json
        except Exception as e:
            print(f"Error al analizar la conversación: {str(e)}")
            return None
    
    def load_conversation(self, conversation_id: str) -> bool:
        """
        Carga una conversación existente.
        
        Args:
            conversation_id (str): ID de la conversación a cargar
        
        Returns:
            bool: True si se cargó correctamente, False en caso contrario
        """
        try:
            conversation_data = storage.load_conversation(conversation_id)
            if conversation_data:
                self.conversation_id = conversation_id
                self.responses = conversation_data["conversation"]["responses"]
                
                # Parsear el análisis guardado
                analysis_json = conversation_data["conversation"].get("analysis")
                if analysis_json:
                    self.analysis = parse_llm_response(json.dumps(analysis_json))
                else:
                    self.analysis = None
                    
                return True
            return False
        except Exception as e:
            print(f"Error al cargar la conversación: {str(e)}")
            return False 