"""
Test script for prompts module functionality.
"""
import sys
from prompts import (
    format_question,
    get_next_question,
    format_analysis_prompt,
    DIAGNOSTIC_QUESTIONS,
    BASE_CONTEXT,
    ANALYSIS_TEMPLATE
)

def main():
    """Run all tests and save output to file."""
    # Redirect output to file
    with open('test_results.txt', 'w', encoding='utf-8') as f:
        sys.stdout = f
        
        print("\nPRUEBAS DEL MÓDULO DE PROMPTS")
        print("\n" + "="*80 + "\n")
        
        # Test 1: Primera pregunta sin respuestas previas
        print("TEST 1: Primera pregunta (sin respuestas previas)")
        print("-" * 50)
        responses = {}
        first_question = get_next_question(responses)
        print("Pregunta inicial:")
        print(f"ID: {first_question['id']}")
        print(f"Pregunta: {first_question['question']}")
        print(f"Propósito: {first_question['purpose']}")
        print("\n" + "="*80 + "\n")
        
        # Test 2: Respuesta con palabra clave de riesgo
        print("TEST 2: Detección de palabras clave de riesgo")
        print("-" * 50)
        responses = {
            "main_concern": "Me siento muy mal, a veces pienso en la muerte"
        }
        risk_question = get_next_question(responses)
        print("Respuesta del usuario con palabra clave de riesgo:")
        print(f"'{responses['main_concern']}'")
        print("\nPregunta priorizada por riesgo:")
        print(f"ID: {risk_question['id']}")
        print(f"Pregunta: {risk_question['question']}")
        print(f"Propósito: {risk_question['purpose']}")
        print(f"Prioridad: {risk_question.get('priority', 'normal')}")
        print("\n" + "="*80 + "\n")
        
        # Test 3: Formateo de prompt final
        print("TEST 3: Formateo del prompt de análisis")
        print("-" * 50)
        responses = {
            "main_concern": "Me siento muy ansioso últimamente",
            "symptoms_duration": "Hace aproximadamente 2 meses",
            "daily_impact": "Me cuesta concentrarme en el trabajo"
        }
        
        print("Respuestas del usuario:")
        for q_id, response in responses.items():
            question = format_question(q_id)
            print(f"\nPregunta: {question['question']}")
            print(f"Respuesta: {response}")
        
        print("\nComponentes del prompt final:")
        print("-" * 30)
        print("1. Contexto base:")
        print(BASE_CONTEXT)
        print("\n2. Respuestas formateadas:")
        responses_text = "\n".join([
            f"Pregunta: {format_question(q_id)['question']}\nRespuesta: {response}"
            for q_id, response in responses.items()
        ])
        print(responses_text)
        print("\n3. Template de análisis:")
        print(ANALYSIS_TEMPLATE)

    # Reset stdout
    sys.stdout = sys.__stdout__
    print("Test completado. Resultados guardados en 'test_results.txt'")

if __name__ == "__main__":
    main() 
