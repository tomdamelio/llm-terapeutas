"""
Test script for storage functionality.
"""
from chatbot import ChatBot
import storage

def test_conversation_storage():
    """Prueba el almacenamiento y carga de conversaciones."""
    print("\n=== Prueba de Almacenamiento de Conversaciones ===\n")
    
    # 1. Realizar una conversación y guardarla
    print("1. Iniciando nueva conversación...")
    bot = ChatBot()
    analysis = bot.run_conversation()
    
    if not bot.conversation_id:
        print("Error: No se generó ID de conversación")
        return
    
    conversation_id = bot.conversation_id
    print(f"\nConversación guardada con ID: {conversation_id}")
    
    # 2. Listar conversaciones recientes
    print("\n2. Listando conversaciones recientes:")
    conversations = storage.list_conversations(limit=5)
    for conv in conversations:
        print(f"\nID: {conv['conversation_id']}")
        print(f"Fecha: {conv['timestamp']}")
        print(f"Versión: {conv['version']}")
    
    # 3. Cargar la conversación guardada
    print("\n3. Intentando cargar la conversación reciente...")
    new_bot = ChatBot()
    if new_bot.load_conversation(conversation_id):
        print("Conversación cargada exitosamente")
        print("\nMostrando resultados de la conversación cargada:")
        new_bot._show_results(new_bot.analysis)
    else:
        print("Error al cargar la conversación")

if __name__ == "__main__":
    test_conversation_storage() 