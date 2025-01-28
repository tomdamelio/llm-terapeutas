"""
Test script for the ChatBot implementation.
"""
from chatbot import ChatBot

def main():
    """
    Función principal para probar el chatbot.
    """
    print("Iniciando prueba del ChatBot...")
    
    try:
        # Crear instancia del chatbot
        bot = ChatBot()
        
        # Ejecutar la conversación
        result = bot.run_conversation()
        
        # Verificar el resultado
        if result:
            print("\nConversación completada exitosamente.")
            print("Resultado del análisis disponible.")
        else:
            print("\nLa conversación fue interrumpida o hubo un error.")
            
    except Exception as e:
        print(f"\nError durante la ejecución: {str(e)}")

if __name__ == "__main__":
    main() 