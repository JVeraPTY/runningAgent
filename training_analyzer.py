"""
Módulo para analizar datos de entrenamiento y generar insights
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import statistics


class TrainingAnalyzer:
    """Analiza datos de entrenamiento y genera métricas"""
    
    def __init__(self, activities: List[Dict]):
        self.activities = activities
        self.running_activities = self._filter_running_activities()
    
    def _filter_running_activities(self) -> List[Dict]:
        """Filtra solo las actividades de running"""
        return [
            activity for activity in self.activities 
            if activity.get('type') in ['Run', 'VirtualRun', 'TrailRun']
        ]
    
    def get_summary_stats(self) -> Dict:
        """Genera estadísticas resumidas del periodo"""
        if not self.running_activities:
            return {
                'total_runs': 0,
                'total_distance_km': 0,
                'total_time_hours': 0,
                'avg_distance_km': 0,
                'avg_pace': 'N/A',
                'total_elevation_gain_m': 0
            }
        
        total_distance = sum(a['distance'] for a in self.running_activities)
        total_time = sum(a['moving_time'] for a in self.running_activities)
        total_elevation = sum(a.get('total_elevation_gain', 0) for a in self.running_activities)
        
        avg_distance = total_distance / len(self.running_activities)
        avg_pace_seconds = total_time / (total_distance / 1000) if total_distance > 0 else 0
        
        return {
            'total_runs': len(self.running_activities),
            'total_distance_km': round(total_distance / 1000, 2),
            'total_time_hours': round(total_time / 3600, 2),
            'avg_distance_km': round(avg_distance / 1000, 2),
            'avg_pace': self._format_pace(avg_pace_seconds),
            'total_elevation_gain_m': round(total_elevation, 0)
        }
    
    def get_weekly_mileage(self) -> List[Dict]:
        """Agrupa actividades por semana y calcula kilometraje"""
        weekly_data = {}
        
        for activity in self.running_activities:
            # Parsear fecha de la actividad
            start_date = datetime.fromisoformat(activity['start_date'].replace('Z', '+00:00'))
            
            # Obtener el lunes de esa semana
            week_start = start_date - timedelta(days=start_date.weekday())
            week_key = week_start.strftime('%Y-%W')
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    'week_start': week_start.strftime('%Y-%m-%d'),
                    'runs': 0,
                    'distance_km': 0,
                    'time_hours': 0,
                    'elevation_m': 0
                }
            
            weekly_data[week_key]['runs'] += 1
            weekly_data[week_key]['distance_km'] += activity['distance'] / 1000
            weekly_data[week_key]['time_hours'] += activity['moving_time'] / 3600
            weekly_data[week_key]['elevation_m'] += activity.get('total_elevation_gain', 0)
        
        # Convertir a lista ordenada por fecha
        weekly_list = sorted(
            weekly_data.values(), 
            key=lambda x: x['week_start'],
            reverse=True
        )
        
        # Redondear valores
        for week in weekly_list:
            week['distance_km'] = round(week['distance_km'], 2)
            week['time_hours'] = round(week['time_hours'], 2)
            week['elevation_m'] = round(week['elevation_m'], 0)
        
        return weekly_list
    
    def analyze_training_load(self) -> Dict:
        """Analiza la carga de entrenamiento y tendencias"""
        weekly_mileage = self.get_weekly_mileage()
        
        if len(weekly_mileage) < 2:
            return {
                'trend': 'insuficiente_data',
                'load_change_percent': 0,
                'is_safe_progression': True,
                'recommendation': 'Necesitas al menos 2 semanas de datos para análisis'
            }
        
        current_week = weekly_mileage[0]['distance_km']
        previous_week = weekly_mileage[1]['distance_km']
        
        if previous_week == 0:
            load_change = 0
        else:
            load_change = ((current_week - previous_week) / previous_week) * 100
        
        # Evaluar si la progresión es segura (regla del 10%)
        is_safe = abs(load_change) <= 10
        
        if load_change > 10:
            trend = 'incremento_rapido'
            recommendation = f'⚠️ Incremento de {load_change:.1f}% - supera la regla del 10%. Riesgo de lesión aumentado.'
        elif load_change < -20:
            trend = 'reduccion_significativa'
            recommendation = f'📉 Reducción de {abs(load_change):.1f}% - considera si estás recuperando o bajando demasiado.'
        elif 0 < load_change <= 10:
            trend = 'progresion_segura'
            recommendation = f'✅ Progresión saludable de {load_change:.1f}% - dentro de límites seguros.'
        elif -20 <= load_change < 0:
            trend = 'semana_descarga'
            recommendation = f'🔄 Semana de descarga con {abs(load_change):.1f}% menos - bueno para recuperación.'
        else:
            trend = 'estable'
            recommendation = '➡️ Volumen estable - mantén la consistencia.'
        
        return {
            'trend': trend,
            'load_change_percent': round(load_change, 1),
            'current_week_km': current_week,
            'previous_week_km': previous_week,
            'is_safe_progression': is_safe,
            'recommendation': recommendation
        }
    
    def get_pace_distribution(self) -> Dict:
        """Analiza distribución de paces para identificar zonas de entrenamiento"""
        if not self.running_activities:
            return {}
        
        paces = []
        for activity in self.running_activities:
            if activity['distance'] > 1000:  # Solo considerar carreras > 1km
                pace_seconds = activity['moving_time'] / (activity['distance'] / 1000)
                paces.append(pace_seconds)
        
        if not paces:
            return {}
        
        avg_pace = statistics.mean(paces)
        median_pace = statistics.median(paces)
        fastest_pace = min(paces)
        slowest_pace = max(paces)
        
        return {
            'avg_pace': self._format_pace(avg_pace),
            'median_pace': self._format_pace(median_pace),
            'fastest_pace': self._format_pace(fastest_pace),
            'slowest_pace': self._format_pace(slowest_pace),
            'pace_variability': round(statistics.stdev(paces) if len(paces) > 1 else 0, 2)
        }
    
    def get_recent_activities_summary(self, limit: int = 5) -> List[Dict]:
        """Obtiene resumen de las últimas actividades"""
        recent = self.running_activities[:limit]
        
        summaries = []
        for activity in recent:
            date = datetime.fromisoformat(activity['start_date'].replace('Z', '+00:00'))
            distance_km = activity['distance'] / 1000
            time_minutes = activity['moving_time'] / 60
            pace = activity['moving_time'] / (activity['distance'] / 1000) if activity['distance'] > 0 else 0
            
            summaries.append({
                'name': activity['name'],
                'date': date.strftime('%Y-%m-%d'),
                'distance_km': round(distance_km, 2),
                'time_minutes': round(time_minutes, 1),
                'pace': self._format_pace(pace),
                'elevation_m': round(activity.get('total_elevation_gain', 0), 0),
                'avg_heartrate': activity.get('average_heartrate'),
                'max_heartrate': activity.get('max_heartrate')
            })
        
        return summaries
    
    def detect_potential_issues(self) -> List[str]:
        """Detecta posibles problemas o riesgos en el entrenamiento"""
        issues = []
        
        # Verificar progresión de carga
        load_analysis = self.analyze_training_load()
        if not load_analysis['is_safe_progression'] and load_analysis['load_change_percent'] > 10:
            issues.append(f"Incremento rápido de volumen ({load_analysis['load_change_percent']:.1f}%)")
        
        # Verificar consistencia
        weekly_mileage = self.get_weekly_mileage()
        if len(weekly_mileage) >= 3:
            distances = [w['distance_km'] for w in weekly_mileage[:3]]
            if statistics.stdev(distances) > statistics.mean(distances) * 0.5:
                issues.append("Alta variabilidad en el kilometraje semanal")
        
        # Verificar frecuencia
        if len(self.running_activities) > 0:
            days_span = (
                datetime.fromisoformat(self.running_activities[0]['start_date'].replace('Z', '+00:00')) -
                datetime.fromisoformat(self.running_activities[-1]['start_date'].replace('Z', '+00:00'))
            ).days
            
            if days_span > 7:
                runs_per_week = len(self.running_activities) / (days_span / 7)
                if runs_per_week < 2:
                    issues.append(f"Baja frecuencia de entrenamiento ({runs_per_week:.1f} carreras/semana)")
        
        return issues if issues else ["No se detectaron problemas significativos"]
    
    @staticmethod
    def _format_pace(pace_seconds: float) -> str:
        """Formatea pace de segundos a MM:SS /km"""
        if pace_seconds == 0:
            return "N/A"
        minutes = int(pace_seconds // 60)
        seconds = int(pace_seconds % 60)
        return f"{minutes}:{seconds:02d} /km"
    
    def generate_training_context(self) -> str:
        """Genera un contexto completo para el agente coach"""
        summary = self.get_summary_stats()
        weekly = self.get_weekly_mileage()
        load = self.analyze_training_load()
        pace_dist = self.get_pace_distribution()
        recent = self.get_recent_activities_summary()
        issues = self.detect_potential_issues()
        
        context = f"""
## DATOS DEL ATLETA

### Resumen General (últimas {summary['total_runs']} carreras)
- Total de carreras: {summary['total_runs']}
- Distancia total: {summary['total_distance_km']} km
- Tiempo total: {summary['total_time_hours']} horas
- Distancia promedio: {summary['avg_distance_km']} km
- Pace promedio: {summary['avg_pace']}
- Desnivel acumulado: {summary['total_elevation_gain_m']} m

### Kilometraje Semanal
"""
        for i, week in enumerate(weekly[:4], 1):
            context += f"Semana {i} ({week['week_start']}): {week['distance_km']} km en {week['runs']} carreras\n"
        
        context += f"""
### Análisis de Carga
- Tendencia: {load['trend']}
- Cambio de volumen: {load['load_change_percent']}%
- {load['recommendation']}

### Distribución de Paces
"""
        if pace_dist:
            context += f"""- Pace promedio: {pace_dist['avg_pace']}
- Pace más rápido: {pace_dist['fastest_pace']}
- Pace más lento: {pace_dist['slowest_pace']}
"""
        
        context += "\n### Últimas 5 Actividades\n"
        for act in recent:
            hr_info = f", FC: {act['avg_heartrate']}-{act['max_heartrate']} bpm" if act['avg_heartrate'] else ""
            context += f"- {act['date']}: {act['name']} - {act['distance_km']} km en {act['time_minutes']} min ({act['pace']}){hr_info}\n"
        
        context += f"\n### Posibles Problemas Detectados\n"
        for issue in issues:
            context += f"- {issue}\n"
        
        return context
