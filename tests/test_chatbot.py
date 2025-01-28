"""
Tests para el sistema de triage en salud mental.
"""
import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

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
        self.assertEqual(len(self.chatbot.chat_history), 1)  # Debe tener el mensaje inicial
    
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
            "No",                 # Sustancias
            "Escucho música"      # Afrontamiento
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
    
    def test_response_processing(self):
        """Test del procesamiento de respuestas."""
        self.chatbot.start_conversation()
        
        # Primera respuesta - preocupación principal
        response = self.chatbot.process_message("Me siento muy triste y ansioso")
        self.assertIn("main_concern", self.chatbot.responses)
        
        # Segunda respuesta - duración
        response = self.chatbot.process_message("Hace dos semanas")
        self.assertIn("duration", self.chatbot.responses)
        
        # Verificar que las respuestas se almacenan correctamente
        self.assertEqual(self.chatbot.responses["main_concern"], "Me siento muy triste y ansioso")
        self.assertEqual(self.chatbot.responses["duration"], "Hace dos semanas")
        
        # Verificar extracción de síntomas
        symptoms = self.chatbot._extract_symptoms(self.chatbot.responses)
        self.assertIn("depressed_mood", symptoms)
        self.assertIn("excessive_worry", symptoms)
    
    def test_diagnosis_generation(self):
        """Test de la generación de diagnósticos."""
        self.chatbot.start_conversation()
        
        # Simular una conversación completa con señales de depresión
        test_responses = [
            "Me siento muy triste y sin esperanza",  # Preocupación principal
            "Más de dos semanas",                    # Duración
            "No puedo trabajar ni concentrarme",     # Impacto diario
            "Me siento deprimido todo el tiempo",    # Cambios de ánimo
            "Casi no duermo",                        # Sueño
            "Tengo familia que me apoya",            # Apoyo
            "No he buscado ayuda antes",            # Ayuda previa
            "No",                                    # Autolesión
            "No",                                    # Sustancias
            "Intento distraerme"                     # Afrontamiento
        ]
        
        # Procesar todas las respuestas
        for response in test_responses:
            result = self.chatbot.process_message(response)
        
        # Verificar que se generó el análisis
        self.assertIsNotNone(self.chatbot.analysis)
        
        # Verificar la estructura del análisis
        analysis = self.chatbot._analyze_responses()
        self.assertIn("urgency_level", analysis)
        self.assertIn("main_concerns", analysis)
        self.assertIn("preliminary_diagnoses", analysis)
        self.assertIn("risk_factors", analysis)
        self.assertIn("protective_factors", analysis)
        self.assertIn("recommendations", analysis)
        
        # Verificar que se identificaron los síntomas correctos
        symptoms = self.chatbot._extract_symptoms(self.chatbot.responses)
        self.assertIn("depressed_mood", symptoms)
        self.assertIn("concentration_problems", symptoms)
        self.assertIn("sleep_changes", symptoms)
        
        # Verificar que se identificaron los factores protectores
        self.assertTrue(any("apoyo" in factor.lower() for factor in analysis["protective_factors"]))

if __name__ == '__main__':
    unittest.main() 