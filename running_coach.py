"""
Agente Coach de Running powered by Claude
"""

import anthropic
from typing import List, Dict, Optional
from training_analyzer import TrainingAnalyzer


class RunningCoach:
    """Agente de coach de running que usa Claude para análisis y consejos"""
    
    def __init__(self, api_key: str, system_prompt: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.system_prompt = system_prompt
        self.conversation_history: List[Dict] = []
        self.training_context: Optional[str] = None
        self.model = "claude-sonnet-4-20250514"
    
    def set_training_context(self, analyzer: TrainingAnalyzer):
        """Establece el contexto de entrenamiento desde el análisis de datos"""
        self.training_context = analyzer.generate_training_context()
    
    def ask(self, question: str, include_context: bool = True) -> str:
        """
        Hace una pregunta al coach
        
        Args:
            question: Pregunta del usuario
            include_context: Si debe incluir el contexto de entrenamiento
        
        Returns:
            str: Respuesta del coach
        """
        # Construir el mensaje del usuario
        user_message = question
        
        # Si es la primera pregunta y hay contexto, incluirlo
        if include_context and self.training_context and len(self.conversation_history) == 0:
            user_message = f"{self.training_context}\n\n---\n\nPregunta del atleta: {question}"
        
        # Agregar mensaje a la historia
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Hacer request a Claude
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=self.system_prompt,
                messages=self.conversation_history
            )
            
            # Extraer respuesta
            assistant_message = response.content[0].text
            
            # Agregar respuesta a la historia
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            return f"Error al comunicarse con el coach: {str(e)}"
    
    def analyze_training(self) -> str:
        """Genera un análisis completo del entrenamiento actual"""
        if not self.training_context:
            return "No hay datos de entrenamiento cargados."
        
        analysis_prompt = """Analiza los datos de entrenamiento proporcionados y genera un reporte completo que incluya:

1. **Evaluación del estado actual**: ¿Cómo está el atleta en términos de volumen, consistencia y progresión?
2. **Fortalezas**: ¿Qué está haciendo bien?
3. **Áreas de mejora**: ¿Qué aspectos necesitan atención?
4. **Recomendaciones específicas**: 3-5 acciones concretas para las próximas semanas
5. **Alertas**: Cualquier señal de riesgo de lesión o sobreentrenamiento

Sé específico, usa los datos concretos y proporciona consejos accionables."""
        
        return self.ask(analysis_prompt, include_context=True)
    
    def predict_race_time(self, distance: str) -> str:
        """Predice tiempo de carrera basado en entrenamientos"""
        question = f"""Basándote en mis entrenamientos recientes, ¿qué tiempo podrías estimar para una carrera de {distance}? 
        
Proporciona:
1. Tiempo estimado conservador
2. Tiempo estimado optimista
3. Pace objetivo recomendado
4. Plan de carrera sugerido"""
        
        return self.ask(question, include_context=True)
    
    def suggest_workout(self, workout_type: str = "general") -> str:
        """Sugiere un entrenamiento específico"""
        question = f"""Sugiere un entrenamiento de tipo '{workout_type}' que sea apropiado para mi nivel actual.
        
Incluye:
1. Calentamiento específico
2. Parte principal con intervalos/ritmos exactos
3. Enfriamiento
4. Objetivo del entrenamiento
5. Zonas de frecuencia cardíaca si es relevante"""
        
        return self.ask(question, include_context=True)
    
    def injury_prevention_tips(self) -> str:
        """Proporciona consejos de prevención de lesiones"""
        question = """Basándote en mi patrón de entrenamiento actual, ¿qué ejercicios de prevención de lesiones me recomiendas?
        
Incluye:
1. Ejercicios de fortalecimiento específicos
2. Trabajo de movilidad
3. Frecuencia recomendada
4. Áreas de riesgo según mi entrenamiento"""
        
        return self.ask(question, include_context=True)
    
    def reset_conversation(self):
        """Reinicia la conversación manteniendo el contexto de entrenamiento"""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> str:
        """Genera un resumen de la conversación"""
        if not self.conversation_history:
            return "No hay conversación activa."
        
        summary_prompt = "Resume los puntos clave de nuestra conversación y las recomendaciones principales que me has dado."
        return self.ask(summary_prompt, include_context=False)


class CoachTools:
    """Herramientas útiles para el coach"""
    
    @staticmethod
    def calculate_training_paces(recent_5k_time_minutes: float) -> Dict[str, str]:
        """
        Calcula paces de entrenamiento basados en un 5K reciente
        Usa fórmulas de Jack Daniels' Running Formula
        
        Args:
            recent_5k_time_minutes: Tiempo de 5K en minutos
        
        Returns:
            Dict con paces para diferentes zonas
        """
        # Pace base en segundos por km
        base_pace_sec = (recent_5k_time_minutes * 60) / 5
        
        # Calcular paces para diferentes zonas (en segundos/km)
        easy_pace = base_pace_sec * 1.25  # 25% más lento
        tempo_pace = base_pace_sec * 1.08  # 8% más lento
        interval_pace = base_pace_sec * 0.96  # 4% más rápido
        repetition_pace = base_pace_sec * 0.90  # 10% más rápido
        
        def format_pace(sec_per_km):
            minutes = int(sec_per_km // 60)
            seconds = int(sec_per_km % 60)
            return f"{minutes}:{seconds:02d} /km"
        
        return {
            'easy': format_pace(easy_pace),
            'tempo': format_pace(tempo_pace),
            'interval': format_pace(interval_pace),
            'repetition': format_pace(repetition_pace),
            'long_run': format_pace(easy_pace * 1.05)
        }
    
    @staticmethod
    def estimate_race_time(distance_km: float, reference_distance_km: float, reference_time_minutes: float) -> float:
        """
        Estima tiempo de carrera usando la fórmula de Riegel
        
        Args:
            distance_km: Distancia objetivo
            reference_distance_km: Distancia de referencia
            reference_time_minutes: Tiempo en la distancia de referencia
        
        Returns:
            Tiempo estimado en minutos
        """
        # Fórmula de Riegel: T2 = T1 * (D2/D1)^1.06
        fatigue_factor = 1.06
        time_ratio = (distance_km / reference_distance_km) ** fatigue_factor
        estimated_time = reference_time_minutes * time_ratio
        
        return estimated_time
    
    @staticmethod
    def calculate_vdot(distance_km: float, time_minutes: float) -> float:
        """
        Calcula VDOT (índice de capacidad aeróbica) según Jack Daniels
        Simplificación de la fórmula completa
        
        Args:
            distance_km: Distancia de la carrera
            time_minutes: Tiempo de la carrera
        
        Returns:
            VDOT estimado
        """
        # Convertir a velocidad en m/min
        velocity_m_min = (distance_km * 1000) / time_minutes
        
        # Fórmula simplificada de VDOT
        # VDOT ≈ -4.6 + 0.182258 * v + 0.000104 * v^2
        vdot = -4.6 + (0.182258 * velocity_m_min) + (0.000104 * velocity_m_min ** 2)
        
        return round(vdot, 1)
