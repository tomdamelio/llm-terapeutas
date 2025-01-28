"""
Module for the ChatBot implementation that handles the conversation flow.
"""
from typing import Dict, Optional
import json

from llm_integration import initialize_llm, send_prompt, process_response
from prompts import (
    get_next_question,
    format_analysis_prompt,
    BASE_CONTEXT
)
import storage

class ChatBot:
    """
    Clase que maneja la conversación con el usuario y la interacción con el LLM.
    """
    
    def __init__(self):
        """Inicializa el chatbot y configura el LLM."""
        self.responses: Dict[str, str] = {}
        self.conversation_active = False
        self.conversation_id: Optional[str] = None
        self.analysis: Optional[Dict] = None
        initialize_llm()
    
    def start_conversation(self) -> None:
        """
        Inicia una nueva conversación con el usuario.
        Muestra el mensaje de bienvenida y prepara el estado inicial.
        """
        self.responses = {}
        self.conversation_active = True
        self.conversation_id = None
        self.analysis = None
        
        print("\n=== Sistema de Triage en Salud Mental ===")
        print("\nBienvenido/a. Voy a hacerte algunas preguntas para entender mejor tu situación.")
        print("Tus respuestas son confidenciales y me ayudarán a determinar el tipo de apoyo que podrías necesitar.")
        print("\nPor favor, responde con la mayor sinceridad posible. Si en algún momento deseas terminar,")
        print("simplemente escribe 'salir'.\n")
    
    def ask_question(self, question_data: Dict) -> str:
        """
        Presenta una pregunta al usuario y obtiene su respuesta.
        
        Args:
            question_data (Dict): Datos de la pregunta a realizar
        
        Returns:
            str: Respuesta del usuario
        """
        print(f"\n{question_data['question']}")
        response = input("> ").strip()
        
        # Verificar si el usuario quiere salir
        if response.lower() in ['salir', 'exit', 'quit']:
            self.conversation_active = False
            return ''
            
        return response
    
    def process_user_input(self, question_id: str, response: str) -> bool:
        """
        Procesa la respuesta del usuario y la almacena.
        
        Args:
            question_id (str): Identificador de la pregunta
            response (str): Respuesta del usuario
        
        Returns:
            bool: True si la respuesta fue procesada correctamente
        """
        if not response:
            return False
            
        self.responses[question_id] = response
        return True
    
    def save_current_conversation(self) -> Optional[str]:
        """
        Guarda la conversación actual en el almacenamiento.
        
        Returns:
            Optional[str]: ID de la conversación guardada o None si hay error
        """
        try:
            conversation_data = {
                "responses": self.responses,
                "analysis": self.analysis
            }
            
            self.conversation_id = storage.save_conversation(conversation_data)
            return self.conversation_id
            
        except Exception as e:
            print(f"\nAdvertencia: No se pudo guardar la conversación: {str(e)}")
            return None
    
    def load_conversation(self, conversation_id: str) -> bool:
        """
        Carga una conversación existente.
        
        Args:
            conversation_id (str): ID de la conversación a cargar
        
        Returns:
            bool: True si la conversación se cargó correctamente
        """
        try:
            data = storage.load_conversation(conversation_id)
            if not data:
                return False
                
            self.conversation_id = conversation_id
            self.responses = data["conversation"]["responses"]
            self.analysis = data["conversation"]["analysis"]
            return True
            
        except Exception as e:
            print(f"\nError al cargar la conversación: {str(e)}")
            return False
    
    def run_conversation(self) -> Optional[Dict]:
        """
        Ejecuta el loop principal de la conversación.
        
        Returns:
            Optional[Dict]: Resultado del análisis o None si la conversación se interrumpe
        """
        self.start_conversation()
        
        while self.conversation_active:
            # Obtener la siguiente pregunta
            next_question = get_next_question(self.responses)
            
            # Si no hay más preguntas, finalizar
            if not next_question:
                break
                
            # Realizar la pregunta y obtener respuesta
            response = self.ask_question(next_question)
            
            # Procesar la respuesta
            if not self.process_user_input(next_question['id'], response):
                break
        
        # Si la conversación terminó normalmente, realizar análisis
        if self.conversation_active and self.responses:
            try:
                # Generar prompt final
                final_prompt = format_analysis_prompt(self.responses)
                
                # Obtener y procesar respuesta del LLM
                llm_response = send_prompt(final_prompt)
                self.analysis = process_response(llm_response)
                
                # Mostrar resultados
                self._show_results(self.analysis)
                
                # Guardar la conversación
                conversation_id = self.save_current_conversation()
                if conversation_id:
                    print(f"\nID de la conversación: {conversation_id}")
                
                return self.analysis
                
            except Exception as e:
                print(f"\nError al procesar el análisis: {str(e)}")
                return None
        
        print("\nGracias por tu tiempo. La conversación ha terminado.")
        return None
    
    def _show_results(self, analysis: Dict) -> None:
        """
        Muestra los resultados del análisis al usuario.
        
        Args:
            analysis (Dict): Resultados del análisis
        """
        print("\n=== Resultados del Análisis ===\n")
        
        # Nivel de urgencia
        urgency = analysis.get('urgency_level', 'DESCONOCIDO')
        print(f"Nivel de Urgencia: {urgency}")
        
        # Principales preocupaciones
        print("\nÁreas principales de preocupación:")
        for concern in analysis.get('main_concerns', []):
            print(f"- {concern}")
        
        # Recomendaciones
        print("\nRecomendaciones:")
        for rec in analysis.get('recommendations', []):
            print(f"- {rec}")
        
        # Factores de riesgo y protección
        if analysis.get('risk_factors'):
            print("\nFactores de riesgo identificados:")
            for factor in analysis['risk_factors']:
                print(f"- {factor}")
        
        if analysis.get('protective_factors'):
            print("\nFactores protectores:")
            for factor in analysis['protective_factors']:
                print(f"- {factor}")
                
        print("\nNota: Este es un análisis preliminar y no constituye un diagnóstico profesional.") 