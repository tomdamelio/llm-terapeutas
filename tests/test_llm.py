"""
Test script for LLM integration functionality.
"""
from llm_integration import initialize_llm, send_prompt, get_model_info

def main():
    print("Testing LLM Integration...")
    
    # Test 1: Initialize LLM
    print("\n1. Testing LLM initialization...")
    try:
        initialize_llm()
        print("✓ LLM initialized successfully")
    except Exception as e:
        print(f"✗ LLM initialization failed: {str(e)}")
        return

    # Test 2: Get Model Info
    print("\n2. Testing model information retrieval...")
    try:
        model_info = get_model_info()
        if model_info:
            print("✓ Available models:")
            for model_name, methods in model_info.items():
                print(f"  - {model_name}: {methods}")
        else:
            print("✗ Could not retrieve model information")
    except Exception as e:
        print(f"✗ Error getting model info: {str(e)}")

    # Test 3: Send a Simple Prompt
    print("\n3. Testing prompt sending...")
    test_prompt = """
    Por favor, responde con un simple 'Hola! El sistema está funcionando correctamente.'
    Responde exactamente con esa frase.
    """
    try:
        response = send_prompt(test_prompt)
        print("✓ Response received:")
        print(f"  {response}")
    except Exception as e:
        print(f"✗ Error sending prompt: {str(e)}")

if __name__ == "__main__":
    main() 