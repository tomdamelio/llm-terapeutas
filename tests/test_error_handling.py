"""
Tests para el manejo de errores en el sistema de triage.
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from chatbot import ChatBot, ChatBotError, InvalidInputError, StorageError, AnalysisError
from diagnosis_parser import AnalysisResult, DiagnosisResult

class TestErrorHandling(unittest.TestCase):
    """Clase de pruebas para el manejo de errores."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.chatbot = ChatBot()
        # Configurar logging para los tests
        self.logger = logging.getLogger('test_error_handling')
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)
    
    def test_invalid_input(self):
        """Test de manejo de entradas inválidas."""
        # Test con mensaje vacío
        self.chatbot.start_conversation()
        result = self.chatbot.process_message("")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "El mensaje no puede estar vacío")
        
        # Test con mensaje demasiado largo
        long_message = "a" * 2000  # Mensaje de 2000 caracteres
        result = self.chatbot.process_message(long_message)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "El mensaje excede el límite de caracteres permitido")
        
        # Test con caracteres inválidos
        invalid_message = "Test\0with\0null\0bytes"
        result = self.chatbot.process_message(invalid_message)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "El mensaje contiene caracteres inválidos")
    
    @patch('storage.save_conversation')
    def test_storage_errors(self, mock_save):
        """Test de errores en el almacenamiento."""
        # Simular error de almacenamiento
        mock_save.side_effect = Exception("Error de almacenamiento")
        
        self.chatbot.start_conversation()
        self.chatbot.process_message("Me siento mal")
        
        # Intentar guardar la conversación
        result = self.chatbot.run_conversation()
        self.assertIsNone(result)
    
    @patch('storage.load_conversation')
    def test_load_conversation_errors(self, mock_load):
        """Test de errores al cargar conversaciones."""
        # Simular error de carga
        mock_load.side_effect = Exception("Error al cargar la conversación")
        
        # Intentar cargar una conversación inexistente
        result = self.chatbot.load_conversation("invalid_id")
        self.assertFalse(result)
    
    def test_malformed_responses(self):
        """Test de manejo de respuestas malformadas."""
        self.chatbot.start_conversation()
        
        # Intentar procesar una respuesta con formato JSON inválido
        invalid_json = "{invalid_json:"
        result = self.chatbot.process_message(invalid_json)
        self.assertNotIn("error", result)  # El chatbot debe manejar esto como texto normal
        
        # Verificar que las respuestas malformadas no rompen el análisis
        analysis = self.chatbot._analyze_responses()
        self.assertIsNotNone(analysis)
    
    @patch('chatbot.ChatBot._analyze_responses')
    def test_analysis_timeout(self, mock_analyze):
        """Test de timeout en el análisis."""
        # Simular timeout en el análisis
        mock_analyze.side_effect = TimeoutError("Análisis tomó demasiado tiempo")
        
        self.chatbot.start_conversation()
        self.chatbot.process_message("Me siento mal")
        
        # Intentar ejecutar el análisis
        result = self.chatbot.run_conversation()
        self.assertIsNone(result)
    
    def test_concurrent_conversations(self):
        """Test de manejo de conversaciones concurrentes."""
        # Iniciar múltiples conversaciones
        chatbot1 = ChatBot()
        chatbot2 = ChatBot()
        
        chatbot1.start_conversation()
        chatbot2.start_conversation()
        
        # Verificar que las conversaciones no interfieren entre sí
        response1 = chatbot1.process_message("Me siento muy triste")
        response2 = chatbot2.process_message("Tengo mucha ansiedad")
        
        # Verificar que las respuestas iniciales son diferentes
        self.assertNotEqual(chatbot1.responses["main_concern"], 
                          chatbot2.responses["main_concern"])
        
        # Continuar las conversaciones de forma diferente
        response1 = chatbot1.process_message("Hace dos semanas")
        response2 = chatbot2.process_message("Desde hace meses")
        
        # Verificar que el estado completo es diferente
        self.assertNotEqual(chatbot1.responses, chatbot2.responses)
        self.assertEqual(len(chatbot1.responses), len(chatbot2.responses))  # Pero tienen la misma estructura
        
        # Verificar que los IDs de conversación son diferentes (si se han generado)
        if chatbot1.conversation_id and chatbot2.conversation_id:
            self.assertNotEqual(chatbot1.conversation_id, chatbot2.conversation_id)

if __name__ == '__main__':
    unittest.main() 
