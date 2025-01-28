"""
Tests para el sistema de triage en salud mental.
"""
import unittest
from datetime import datetime
from chatbot import ChatBot
from diagnosis_parser import AnalysisResult, DiagnosisResult

class TestChatBot(unittest.TestCase):
    """Clase de pruebas para el ChatBot."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.chatbot = ChatBot()
    
    def test_chatbot_initialization(self):
        """Test de inicialización del chatbot."""
        self.chatbot.start_conversation()
        self.assertTrue(self.chatbot.conversation_active)
        self.assertEqual(self.chatbot.responses, {})
        self.assertIsNone(self.chatbot.conversation_id)
        self.assertIsNone(self.chatbot.analysis)
    
    def test_question_flow(self):
        """Test del flujo de preguntas."""
        self.chatbot.start_conversation()
        
        # Simular una conversación completa
        responses = [
            "Me siento muy mal",  # Respuesta inicial
            "Hace dos semanas",   # Duración
            "No puedo trabajar",  # Impacto diario
            "Sí, muchos cambios", # Cambios de ánimo
            "Duermo mal",         # Sueño
            "No tengo apoyo",     # Apoyo
            "No",                 # Ayuda previa
            "No",                 # Autolesión
            "No",                # Sustancias
            "Escucho música"     # Afrontamiento
        ]
        
        previous_questions = set()
        for response in responses:
            result = self.chatbot.process_message(response)
            
            # Verificar que la respuesta tiene el formato correcto
            self.assertIn("message", result)
            
            # Si no es el mensaje final de análisis
            if "analysis" not in result:
                current_question = result["message"]
                # Verificar que la pregunta no se repite
                self.assertNotIn(current_question, previous_questions)
                previous_questions.add(current_question)
    
    def test_response_tracking(self):
        """Test del seguimiento de respuestas."""
        self.chatbot.start_conversation()
        
        # Primera respuesta
        response = self.chatbot.process_message("Me siento muy mal")
        self.assertIn("main_concern", self.chatbot.responses)
        
        # Segunda respuesta
        response = self.chatbot.process_message("Hace dos semanas")
        self.assertIn("duration", self.chatbot.responses)
        self.assertEqual(len(self.chatbot.responses), 2)
        
        # Verificar que las respuestas se almacenan correctamente
        self.assertEqual(self.chatbot.responses["main_concern"], "Me siento muy mal")
        self.assertEqual(self.chatbot.responses["duration"], "Hace dos semanas")
    
    def test_risk_detection(self):
        """Test de detección de riesgo y priorización de preguntas."""
        self.chatbot.start_conversation()
        
        # Enviar mensaje con señales de riesgo
        response = self.chatbot.process_message("Quiero morirme")
        
        # Verificar que la siguiente pregunta es sobre autolesión
        self.assertIn("¿Has tenido pensamientos", response["message"])
        self.assertIn("daño", response["message"].lower())
    
    def test_no_repeated_questions(self):
        """Test específico para verificar que no se repiten preguntas."""
        self.chatbot.start_conversation()
        
        # Mantener registro de todas las preguntas realizadas
        questions_asked = []
        
        # Simular una conversación corta
        responses = ["Me siento mal", "Hace un mes", "No puedo trabajar"]
        
        for response in responses:
            result = self.chatbot.process_message(response)
            if "message" in result:
                question = result["message"]
                # Verificar que la pregunta no está en el historial
                self.assertNotIn(question, questions_asked)
                questions_asked.append(question)
        
        # Verificar que el número de preguntas únicas coincide con el número de respuestas
        self.assertEqual(len(set(questions_asked)), len(questions_asked))

    def test_response_processing(self):
        """Test del procesamiento de respuestas."""
        self.chatbot.start_conversation()
        
        # Procesar una respuesta
        response = self.chatbot.process_message("Me siento muy triste y ansioso")
        self.assertIn("main_concern", self.chatbot.responses)
        
        # Verificar extracción de síntomas
        symptoms = self.chatbot._extract_symptoms(self.chatbot.responses)
        self.assertIn("depressed_mood", symptoms)
        
        # Procesar más respuestas
        response = self.chatbot.process_message("No puedo dormir")
        symptoms = self.chatbot._extract_symptoms(self.chatbot.responses)
        self.assertIn("sleep_changes", symptoms)
    
    def test_diagnosis_generation(self):
        """Test de la generación de diagnósticos."""
        self.chatbot.start_conversation()
        
        # Simular una conversación completa con señales de depresión
        test_responses = [
            "Me siento muy triste y sin esperanza",
            "Más de dos semanas",
            "No puedo trabajar ni concentrarme",
            "Me siento deprimido todo el tiempo",
            "Casi no duermo",
            "Tengo familia que me apoya",
            "No he buscado ayuda antes",
            "No",
            "No",
            "Intento distraerme"
        ]
        
        # Procesar todas las respuestas
        for response in test_responses:
            result = self.chatbot.process_message(response)
        
        # Generar análisis
        analysis = self.chatbot._analyze_responses()
        
        # Verificar estructura del análisis
        self.assertIn("urgency_level", analysis)
        self.assertIn("main_concerns", analysis)
        self.assertIn("preliminary_diagnoses", analysis)
        self.assertIn("risk_factors", analysis)
        self.assertIn("protective_factors", analysis)
        self.assertIn("recommendations", analysis)

if __name__ == '__main__':
    unittest.main() 