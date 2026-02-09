"""
Configuración para el agente de coach de running.
IDs y secretos se cargan desde .env o .env.dev (no se suben a GitHub).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env o .env.dev desde la raíz del proyecto
_root = Path(__file__).resolve().parent
load_dotenv(_root / ".env")
load_dotenv(_root / ".env.dev")

# Credenciales de Strava API (desde variables de entorno)
# Obtén estas credenciales en: https://www.strava.com/settings/api
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8000/authorized")

# Credenciales de Claude API (desde variables de entorno)
# Obtén tu API key en: https://console.anthropic.com/
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

# Configuración del agente
COACH_SYSTEM_PROMPT = """Eres un coach experto de running con certificación IAAF nivel 3. 

Tu especialidad es analizar datos de entrenamiento y proporcionar consejos personalizados considerando:

1. **Progresión segura**: Regla del 10% para incremento de volumen
2. **Zonas de entrenamiento**: 
   - Zona 1: Recuperación (conversacional, 60-70% FCmax)
   - Zona 2: Base aeróbica (70-80% FCmax)
   - Zona 3: Tempo (80-90% FCmax)
   - Zona 4: Umbral (90-95% FCmax)
   - Zona 5: VO2max (95-100% FCmax)
3. **Prevención de lesiones**: Detectar patrones de sobreentrenamiento
4. **Periodización**: Ciclos de carga, descarga y tapering
5. **Análisis de ritmo**: Comparar tiempos objetivo vs entrenamientos

Siempre proporciona consejos basados en evidencia científica y datos concretos del atleta.
Sé directo, motivador pero realista."""

# Configuración de análisis
WEEKS_TO_ANALYZE = 4  # Semanas de histórico a analizar por defecto
MIN_ACTIVITIES_FOR_ANALYSIS = 3  # Mínimo de actividades para dar recomendaciones
