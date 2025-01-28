# Project overview

Este proyecto consiste en desarrollar una solución de triage inicial en salud mental utilizando un modelo de lenguaje (LLM) y una interfaz sencilla de chatbot. El objetivo es que el usuario responda alrededor de 10 preguntas básicas, y al finalizar el cuestionario, se ofrezca una evaluación preliminar con hasta tres posibles diagnósticos (o categorías de riesgo). Además, se busca identificar casos de urgencia para recomendar asistencia inmediata.  
La Fase 0 contempla un MVP con interfaz mínima (por terminal o muy simple GUI), mientras que la Fase 1 incluye mejorar la experiencia de usuario y generar reportes automatizados para profesionales, ofreciendo una primera integración con servicios externos.  
La meta es validar la funcionalidad principal de triage, recopilar feedback de usuarios y profesionales, y sentar las bases para integraciones futuras (por ejemplo, análisis emocional multimodal y derivaciones automatizadas).


# Core functionalities

A continuación se detallan las funcionalidades clave, organizadas por fases y en tareas secuenciales para el equipo de desarrollo.  

## Fase 0: MVP básico de triage
    
1. **Setup del entorno y configuración del proyecto**  
   1.1. Crear el repositorio en Git (p.ej. GitHub)  
       1.1.1. Inicializar repositorio local con `git init`
       1.1.2. Crear repositorio remoto en GitHub
       1.1.3. Conectar repositorio local con remoto usando `git remote add origin <url>`
       1.1.4. Crear archivo `.gitignore` para excluir archivos sensibles
   1.2. Definir el archivo `requirements.txt` con las librerías iniciales
       1.2.1. Crear archivo `requirements.txt` en la raíz del proyecto
       1.2.2. Añadir dependencias base: `openai`, `google-generativeai`, `python-dotenv`
       1.2.3. Especificar versiones exactas de cada librería
   1.3. Generar una estructura base de archivos para el proyecto
       1.3.1. Crear directorio `src/` para código fuente
       1.3.2. Crear directorio `tests/` para pruebas unitarias
       1.3.3. Crear directorio `config/` para archivos de configuración
       1.3.4. Crear archivo `main.py` como punto de entrada
       1.3.5. Crear archivo `.env` para variables de entorno

2. **Integración con un LLM "barato"**  
   2.1. Configurar el acceso a la API del modelo de lenguaje
       2.1.1. Crear cuenta en Google Cloud Platform
       2.1.2. Generar API key para Gemini
       2.1.3. Almacenar API key en archivo `.env`
       2.1.4. Crear módulo `config.py` para cargar variables de entorno
   2.2. Crear módulo `llm_integration.py`
       2.2.1. Implementar función `initialize_llm()` para setup inicial
       2.2.2. Implementar función `send_prompt(prompt: str) -> str`
       2.2.3. Implementar función `process_response(response: str) -> dict`
       2.2.4. Implementar manejo de errores y reintentos
   2.3. Definir prompt inicial y flujo de preguntas
       2.3.1. Crear archivo `prompts.py` con templates de prompts
       2.3.2. Definir prompt base con contexto médico
       2.3.3. Crear lista de 10 preguntas diagnósticas
       2.3.4. Implementar función para formatear preguntas

3. **Construcción del chatbot (interfaz mínima)**  
   3.1. Implementar versión CLI
       3.1.1. Crear clase `ChatBot` en `chatbot.py`
       3.1.2. Implementar método `start_conversation()`
       3.1.3. Implementar método `ask_question(question: str) -> str`
       3.1.4. Implementar método `process_user_input(input: str) -> bool`
       3.1.5. Implementar loop principal de conversación
   3.2. Añadir sistema de almacenamiento
       3.2.1. Crear módulo `storage.py`
       3.2.2. Implementar función `save_conversation(conversation: dict)`
       3.2.3. Implementar función `load_conversation(conversation_id: str)`
       3.2.4. Definir estructura JSON para conversaciones
   3.3. Implementar componente web minimalista
       3.3.1. Crear archivo `app.py` con Flask/FastAPI
       3.3.2. Crear template HTML básico para chat
       3.3.3. Implementar endpoint POST para mensajes
       3.3.4. Implementar endpoint GET para historial

4. **Generación de lista de posibles diagnósticos**  
   4.1. Diseñar prompt final
       4.1.1. Crear template para análisis de respuestas
       4.1.2. Definir formato estructurado para diagnósticos
       4.1.3. Implementar sistema de pesos para síntomas
       4.1.4. Crear reglas de validación de diagnósticos
   4.2. Implementar parser de respuestas
       4.2.1. Crear módulo `diagnosis_parser.py`
       4.2.2. Implementar función `parse_llm_response(response: str) -> list`
       4.2.3. Implementar función `format_diagnosis(diagnosis: list) -> str`
       4.2.4. Añadir validaciones de formato

5. **Incluir unit tests necesarios**  
   5.1. Crear tests para el flujo
       5.1.1. Implementar `test_chatbot_initialization()`
       5.1.2. Implementar `test_question_flow()`
       5.1.3. Implementar `test_response_processing()`
       5.1.4. Implementar `test_diagnosis_generation()`
   5.2. Implementar manejo de errores
       5.2.1. Crear casos de prueba para errores de API
       5.2.2. Crear casos de prueba para entradas inválidas
       5.2.3. Crear casos de prueba para timeouts
       5.2.4. Implementar logging de errores


## Fase 1: Prototipo con interfaz mejorada y reportes

1. **Diseño UI/UX mejorado**  
   1.1. Crear un frontend simple (HTML/CSS + un framework ligero como Bootstrap o Tailwind) para mostrar el chatbot en estilo “ventana de conversación”.  
   1.2. Añadir navegación básica (pantalla de bienvenida, pantalla del chatbot, pantalla de resultados).

2. **Reporte automatizado para terapeutas**  
   2.1. Generar un módulo (`report_generator.py`) que compile:  
       - Resumen de respuestas relevantes.  
       - Urgencia detectada (sí/no).  
       - Hasta 3 posibles diagnósticos o categorías.  
   2.2. Formatear ese contenido (PDF o HTML) y guardarlo localmente o enviarlo por email (si se requiere).  
   2.3. Verificar cumplimiento de privacidad (mecanismos de encriptado, disclaimers, etc.).

3. **Opciones de integración**  
   3.1. Crear endpoints (por ejemplo, en `app.py`) para exponer la funcionalidad de triage como API REST.  
       - Endpoint `POST /triage` que reciba respuestas de usuario y devuelva resultados.  
   3.2. Testear la integración con servicios de mensajería (p.ej. Slack/WhatsApp), si aplica.

4. **Evaluación de urgencia/riesgo**  
   5.1. Incluir checks básicos (palabras clave de ideación suicida, nivel de malestar extremo, etc.).  
   5.2. Si se detecta urgencia, el sistema muestra aviso de “Consulta inmediata a un profesional” o “Línea de ayuda”.  
   5.3. Incorporar guardrails en el prompt para reducir el riesgo de respuestas inadecuadas o peligrosas.

5. **Testing de usabilidad y recolección de métricas**  
   4.1. Añadir Google Analytics o herramienta similar para medir uso, tasa de finalización del cuestionario, etc.  
   4.2. Realizar pruebas con usuarios externos (pacientes y profesionales) en escenarios controlados.  
   4.3. Recopilar feedback para la siguiente iteración.

# Doc

### Librerías requeridas (ejemplo `requirements.txt`)

openai==0.27.0
flask==2.3.2
pydantic==1.10.7
pdfkit==1.0.0 # para generar reportes en PDF (opcional)
requests==2.28.1


### Configuración de OpenAI API (ejemplo)

    ```python

    import openai
    
    openai.api_key = "YOUR_OPENAI_API_KEY"
    
    def generate_response(prompt):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=256,
            temperature=0.7
        )
        return response.choices[0].text.strip()

    ```

### Ejemplo de flujo de preguntas (pseudo-código)

    ```python

    def triage_conversation():
        questions = [
            "¿Cuál es tu principal motivo de consulta?",
            "¿Desde cuándo presentas estos síntomas?",
            "¿Cómo describirías tu nivel de malestar?",
            # ...
        ]
        user_responses = []
        
        for q in questions:
            user_input = input(q + "\n> ")
            user_responses.append(user_input)
    
    # Generar prompt final
    summary_prompt = f"""
    Eres un asistente clínico especializado en salud mental. 
    Basado en las siguientes respuestas del usuario, sugiere 2 o 3 posibles diagnósticos y un indicador de urgencia.

    Respuestas:
    1) {user_responses[0]}
    2) {user_responses[1]}
    ...

    Formato de respuesta:
    3) Diagnóstico 1
    4) Diagnóstico 2
    5) Diagnóstico 3 (opcional)
    Urgencia: leve / moderada / alta
    """
    
    result = generate_response(summary_prompt)
    print("Resultados preliminares:\n", result)

    ```

### Generación de reporte (idea en Python)

    ```python

    import pdfkit
    
    def generate_report(diagnosis_summary, user_responses):
        html_content = f"""
        <h1>Reporte de Triage Mental</h1>
        <p><strong>Diagnósticos potenciales:</strong></p>
        <pre>{diagnosis_summary}</pre>
        <p><strong>Respuestas del usuario:</strong></p>
        <ul>
        {''.join(f'<li>{resp}</li>' for resp in user_responses)}
        </ul>
        """
        pdfkit.from_string(html_content, "triage_report.pdf")
        print("Reporte generado: triage_report.pdf")

    ```

# Current file structure
mental-llm-triage/
├── src/
│   ├── __init__.py
│   ├── app.py                 # Archivo principal de Flask/FastAPI
│   ├── llm_integration.py     # Funciones para interactuar con la API del LLM
│   ├── chatbot_flow.py        # Lógica de conversación (preguntas, manejo de respuestas)
│   ├── report_generator.py    # Funciones para generar reporte PDF/HTML
│   └── utils.py               # Utilidades generales (parseos, validaciones, etc.)
├── templates/
│   ├── base.html              # Template base (HTML)
│   ├── chatbot.html           # Interfaz para el chatbot
│   └── report.html            # Template para el reporte en HTML
├── static/
│   ├── css/
│   │   └── styles.css         # Estilos para la interfaz
│   └── js/
│       └── chatbot.js         # Lógica de frontend si se requiere
├── data/
│   └── sample_conversations/  # Almacena logs de conversaciones (JSON, etc.)
├── tests/
│   ├── test_app.py            # Pruebas unitarias e2e
│   ├── test_llm_integration.py
│   └── test_report_generator.py
├── requirements.txt
└── README.md
