"""
Module for parsing and formatting diagnosis responses from the LLM.
"""
import json
from typing import Dict, List, Union, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DiagnosisResult:
    """Estructura de datos para un diagnóstico."""
    condition: str
    confidence: float
    key_indicators: List[str]
    severity: str = "No especificada"
    duration: Optional[int] = None  # en días

@dataclass
class AnalysisResult:
    """Estructura de datos para el análisis completo."""
    urgency_level: str
    main_concerns: List[str]
    preliminary_diagnoses: List[DiagnosisResult]
    risk_factors: List[str]
    protective_factors: List[str]
    recommendations: List[str]
    timestamp: datetime = datetime.now()

def validate_urgency_level(level: str) -> bool:
    """
    Valida que el nivel de urgencia sea válido.
    
    Args:
        level (str): Nivel de urgencia a validar
    
    Returns:
        bool: True si es válido, False en caso contrario
    """
    return level.upper() in ["ALTO", "MEDIO", "BAJO"]

def validate_diagnosis_format(diagnosis: Dict) -> bool:
    """
    Valida que un diagnóstico tenga el formato correcto.
    
    Args:
        diagnosis (Dict): Diagnóstico a validar
    
    Returns:
        bool: True si el formato es válido, False en caso contrario
    """
    required_fields = ["condition", "confidence", "key_indicators"]
    
    # Verificar campos requeridos
    if not all(field in diagnosis for field in required_fields):
        return False
    
    # Validar tipos de datos
    try:
        # Convertir confidence a float si viene como string
        if isinstance(diagnosis["confidence"], str):
            confidence = float(diagnosis["confidence"].rstrip("%"))
            if not 0 <= confidence <= 100:
                return False
        elif isinstance(diagnosis["confidence"], (int, float)):
            if not 0 <= diagnosis["confidence"] <= 100:
                return False
        else:
            return False
        
        # Validar otros campos
        if not isinstance(diagnosis["condition"], str):
            return False
        if not isinstance(diagnosis["key_indicators"], list):
            return False
        if not all(isinstance(i, str) for i in diagnosis["key_indicators"]):
            return False
            
        return True
    except (ValueError, TypeError):
        return False

def parse_llm_response(response: str) -> Optional[AnalysisResult]:
    """
    Parsea la respuesta del LLM y la convierte en una estructura de datos validada.
    
    Args:
        response (str): Respuesta JSON del LLM
    
    Returns:
        Optional[AnalysisResult]: Resultado del análisis parseado o None si hay error
    """
    try:
        # Intentar parsear el JSON
        data = json.loads(response)
        
        # Validar campos requeridos
        required_fields = [
            "urgency_level",
            "main_concerns",
            "preliminary_diagnoses",
            "risk_factors",
            "protective_factors",
            "recommendations"
        ]
        
        if not all(field in data for field in required_fields):
            raise ValueError("Faltan campos requeridos en la respuesta")
        
        # Validar nivel de urgencia
        if not validate_urgency_level(data["urgency_level"]):
            raise ValueError("Nivel de urgencia inválido")
        
        # Validar y convertir diagnósticos
        diagnoses = []
        for diag in data["preliminary_diagnoses"]:
            if not validate_diagnosis_format(diag):
                raise ValueError(f"Formato inválido en diagnóstico: {diag}")
            
            # Convertir confidence a float si es string
            confidence = diag["confidence"]
            if isinstance(confidence, str):
                confidence = float(confidence.rstrip("%"))
            
            diagnoses.append(DiagnosisResult(
                condition=diag["condition"],
                confidence=confidence,
                key_indicators=diag["key_indicators"],
                severity=diag.get("severity", "No especificada"),
                duration=diag.get("duration")
            ))
        
        # Crear y retornar el resultado
        return AnalysisResult(
            urgency_level=data["urgency_level"].upper(),
            main_concerns=data["main_concerns"],
            preliminary_diagnoses=diagnoses,
            risk_factors=data["risk_factors"],
            protective_factors=data["protective_factors"],
            recommendations=data["recommendations"]
        )
        
    except json.JSONDecodeError:
        print("Error al decodificar JSON de la respuesta")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error al parsear la respuesta: {str(e)}")
        return None
    except Exception as e:
        print(f"Error inesperado al parsear la respuesta: {str(e)}")
        return None

def format_diagnosis(analysis: AnalysisResult) -> str:
    """
    Formatea el resultado del análisis en un texto legible.
    
    Args:
        analysis (AnalysisResult): Resultado del análisis a formatear
    
    Returns:
        str: Texto formateado con el análisis
    """
    # Formatear nivel de urgencia
    urgency_text = {
        "ALTO": "⚠️ ALTO - Requiere atención inmediata",
        "MEDIO": "⚡ MEDIO - Requiere atención próxima",
        "BAJO": "ℹ️ BAJO - Puede esperar atención regular"
    }
    
    # Construir las secciones del texto
    sections = []
    
    # Encabezado
    sections.append("EVALUACIÓN PRELIMINAR DE SALUD MENTAL")
    sections.append("=====================================")
    sections.append("")
    
    # Nivel de urgencia
    sections.append(f"Nivel de Urgencia: {urgency_text.get(analysis.urgency_level, analysis.urgency_level)}")
    sections.append("")
    
    # Preocupaciones principales
    sections.append("Preocupaciones Principales:")
    sections.append("--------------------------")
    for concern in analysis.main_concerns:
        sections.append(f"• {concern}")
    sections.append("")
    
    # Diagnósticos preliminares
    sections.append("Diagnósticos Preliminares:")
    sections.append("-------------------------")
    for diag in analysis.preliminary_diagnoses:
        sections.append(f"• {diag.condition} (Confianza: {diag.confidence:.0f}%)")
        sections.append(f"  Indicadores: {', '.join(diag.key_indicators)}")
    sections.append("")
    
    # Factores de riesgo
    sections.append("Factores de Riesgo:")
    sections.append("------------------")
    for factor in analysis.risk_factors:
        sections.append(f"• {factor}")
    sections.append("")
    
    # Factores protectores
    sections.append("Factores Protectores:")
    sections.append("--------------------")
    for factor in analysis.protective_factors:
        sections.append(f"• {factor}")
    sections.append("")
    
    # Recomendaciones
    sections.append("Recomendaciones:")
    sections.append("---------------")
    for rec in analysis.recommendations:
        sections.append(f"• {rec}")
    sections.append("")
    
    # Nota final
    sections.append("Nota: Esta es una evaluación preliminar y no constituye un diagnóstico profesional.")
    sections.append(f"Fecha de evaluación: {analysis.timestamp.strftime('%d/%m/%Y %H:%M')}")
    
    return "\n".join(sections)

def format_json_response(analysis: AnalysisResult) -> Dict:
    """
    Convierte el resultado del análisis en un formato JSON para la API.
    
    Args:
        analysis (AnalysisResult): Resultado del análisis a formatear
    
    Returns:
        Dict: Diccionario con el formato requerido por la API
    """
    return {
        "urgency_level": analysis.urgency_level,
        "main_concerns": analysis.main_concerns,
        "preliminary_diagnoses": [
            {
                "condition": d.condition,
                "confidence": f"{d.confidence:.0f}%",
                "key_indicators": d.key_indicators,
                "severity": d.severity,
                "duration": d.duration
            }
            for d in analysis.preliminary_diagnoses
        ],
        "risk_factors": analysis.risk_factors,
        "protective_factors": analysis.protective_factors,
        "recommendations": analysis.recommendations,
        "timestamp": analysis.timestamp.isoformat()
    } 