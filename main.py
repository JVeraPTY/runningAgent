#!/usr/bin/env python3
"""
Running Coach Agent - Aplicación Principal
Coach de running personal powered by Strava + Claude
"""

import sys
from datetime import datetime, timedelta
from config import (
    STRAVA_CLIENT_ID,
    STRAVA_CLIENT_SECRET, 
    STRAVA_REDIRECT_URI,
    CLAUDE_API_KEY,
    COACH_SYSTEM_PROMPT,
    WEEKS_TO_ANALYZE
)
from strava_client import (
    authenticate_strava,
    StravaClient,
    meters_to_km,
    seconds_to_time,
    calculate_pace
)
from training_analyzer import TrainingAnalyzer
from running_coach import RunningCoach, CoachTools


class RunningCoachApp:
    """Aplicación principal del coach de running"""
    
    def __init__(self):
        self.strava_client = None
        self.coach = None
        self.analyzer = None
        self.athlete = None
    
    def initialize(self):
        """Inicializa la aplicación y se conecta a Strava y Claude"""
        print("=" * 60)
        print("🏃 RUNNING COACH AGENT")
        print("Powered by Strava + Claude")
        print("=" * 60)
        
        # Autenticar con Strava
        try:
            auth = authenticate_strava(
                STRAVA_CLIENT_ID,
                STRAVA_CLIENT_SECRET,
                STRAVA_REDIRECT_URI
            )
            self.strava_client = StravaClient(auth)
            
            # Obtener información del atleta
            self.athlete = self.strava_client.get_athlete()
            print(f"✓ Conectado como: {self.athlete['firstname']} {self.athlete['lastname']}")
            
        except Exception as e:
            print(f"✗ Error al conectar con Strava: {e}")
            sys.exit(1)
        
        # Cargar datos de entrenamiento
        try:
            print(f"\n📊 Cargando datos de las últimas {WEEKS_TO_ANALYZE} semanas...")
            after_date = datetime.now() - timedelta(weeks=WEEKS_TO_ANALYZE)
            activities = self.strava_client.get_activities(after=after_date)
            
            print(f"✓ Se cargaron {len(activities)} actividades")
            
            # Analizar datos
            self.analyzer = TrainingAnalyzer(activities)
            running_count = len(self.analyzer.running_activities)
            print(f"✓ Detectadas {running_count} actividades de running")
            
        except Exception as e:
            print(f"✗ Error al cargar datos: {e}")
            sys.exit(1)
        
        # Inicializar coach con Claude
        try:
            print("\n🤖 Inicializando coach con Claude...")
            self.coach = RunningCoach(CLAUDE_API_KEY, COACH_SYSTEM_PROMPT)
            self.coach.set_training_context(self.analyzer)
            print("✓ Coach listo para ayudarte\n")
            
        except Exception as e:
            print(f"✗ Error al inicializar coach: {e}")
            sys.exit(1)
    
    def show_menu(self):
        """Muestra el menú principal"""
        print("\n" + "=" * 60)
        print("MENÚ PRINCIPAL")
        print("=" * 60)
        print("1. Ver resumen de entrenamiento")
        print("2. Análisis completo del coach")
        print("3. Predecir tiempo de carrera")
        print("4. Sugerir entrenamiento")
        print("5. Consejos de prevención de lesiones")
        print("6. Hacer pregunta al coach")
        print("7. Calcular paces de entrenamiento")
        print("8. Ver estadísticas de Strava")
        print("9. Salir")
        print("=" * 60)
    
    def show_training_summary(self):
        """Muestra resumen de entrenamiento"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE ENTRENAMIENTO")
        print("=" * 60)
        
        summary = self.analyzer.get_summary_stats()
        print(f"\nÚltimas {summary['total_runs']} carreras:")
        print(f"  • Distancia total: {summary['total_distance_km']} km")
        print(f"  • Tiempo total: {summary['total_time_hours']} horas")
        print(f"  • Distancia promedio: {summary['avg_distance_km']} km")
        print(f"  • Pace promedio: {summary['avg_pace']}")
        print(f"  • Desnivel total: {summary['total_elevation_gain_m']} m")
        
        print("\n📅 Kilometraje Semanal:")
        weekly = self.analyzer.get_weekly_mileage()
        for i, week in enumerate(weekly[:4], 1):
            print(f"  Semana {i} ({week['week_start']}): {week['distance_km']} km - {week['runs']} carreras")
        
        print("\n📈 Análisis de Carga:")
        load = self.analyzer.analyze_training_load()
        print(f"  • Cambio de volumen: {load['load_change_percent']}%")
        print(f"  • {load['recommendation']}")
        
        print("\n🎯 Distribución de Paces:")
        pace_dist = self.analyzer.get_pace_distribution()
        if pace_dist:
            print(f"  • Promedio: {pace_dist['avg_pace']}")
            print(f"  • Más rápido: {pace_dist['fastest_pace']}")
            print(f"  • Más lento: {pace_dist['slowest_pace']}")
        
        print("\n⚠️  Problemas Detectados:")
        issues = self.analyzer.detect_potential_issues()
        for issue in issues:
            print(f"  • {issue}")
    
    def get_coach_analysis(self):
        """Obtiene análisis completo del coach"""
        print("\n🤖 Generando análisis del coach...")
        print("=" * 60)
        
        analysis = self.coach.analyze_training()
        print(f"\n{analysis}")
    
    def predict_race(self):
        """Predice tiempo de carrera"""
        print("\n🏁 PREDICCIÓN DE CARRERA")
        print("=" * 60)
        
        distances = {
            '1': '5K',
            '2': '10K',
            '3': 'Media Maratón',
            '4': 'Maratón'
        }
        
        print("\nSelecciona la distancia:")
        for key, dist in distances.items():
            print(f"{key}. {dist}")
        
        choice = input("\nOpción: ").strip()
        distance = distances.get(choice, '10K')
        
        print(f"\n🤖 Analizando para {distance}...")
        prediction = self.coach.predict_race_time(distance)
        print(f"\n{prediction}")
    
    def suggest_workout(self):
        """Sugiere un entrenamiento"""
        print("\n💪 SUGERENCIA DE ENTRENAMIENTO")
        print("=" * 60)
        
        workout_types = {
            '1': 'intervalos',
            '2': 'tempo',
            '3': 'carrera larga',
            '4': 'recuperación',
            '5': 'fartlek'
        }
        
        print("\nTipo de entrenamiento:")
        for key, wtype in workout_types.items():
            print(f"{key}. {wtype.capitalize()}")
        
        choice = input("\nOpción: ").strip()
        workout_type = workout_types.get(choice, 'general')
        
        print(f"\n🤖 Generando plan de {workout_type}...")
        suggestion = self.coach.suggest_workout(workout_type)
        print(f"\n{suggestion}")
    
    def get_injury_prevention(self):
        """Obtiene consejos de prevención de lesiones"""
        print("\n🩹 PREVENCIÓN DE LESIONES")
        print("=" * 60)
        print("\n🤖 Generando recomendaciones...")
        
        tips = self.coach.injury_prevention_tips()
        print(f"\n{tips}")
    
    def chat_with_coach(self):
        """Modo de chat libre con el coach"""
        print("\n💬 CHAT CON EL COACH")
        print("=" * 60)
        print("Escribe 'salir' para volver al menú\n")
        
        while True:
            question = input("Tu pregunta: ").strip()
            
            if question.lower() in ['salir', 'exit', 'quit']:
                break
            
            if not question:
                continue
            
            print("\n🤖 Coach:")
            response = self.coach.ask(question)
            print(f"{response}\n")
    
    def calculate_training_paces(self):
        """Calcula paces de entrenamiento"""
        print("\n⏱️  CALCULADORA DE PACES")
        print("=" * 60)
        
        try:
            time_str = input("\n¿Cuál es tu mejor tiempo de 5K? (formato MM:SS): ").strip()
            minutes, seconds = map(int, time_str.split(':'))
            total_minutes = minutes + (seconds / 60)
            
            paces = CoachTools.calculate_training_paces(total_minutes)
            
            print("\n🎯 Paces de Entrenamiento Recomendados:")
            print(f"  • Easy/Recuperación: {paces['easy']}")
            print(f"  • Long Run: {paces['long_run']}")
            print(f"  • Tempo: {paces['tempo']}")
            print(f"  • Intervalos: {paces['interval']}")
            print(f"  • Repeticiones: {paces['repetition']}")
            
        except ValueError:
            print("✗ Formato inválido. Usa MM:SS (ej: 22:30)")
    
    def show_strava_stats(self):
        """Muestra estadísticas de Strava"""
        print("\n📈 ESTADÍSTICAS DE STRAVA")
        print("=" * 60)
        
        try:
            stats = self.strava_client.get_activity_stats()
            
            recent_run = stats.get('recent_run_totals', {})
            all_run = stats.get('all_run_totals', {})
            
            print("\n🏃 Últimos 4 semanas:")
            print(f"  • Carreras: {recent_run.get('count', 0)}")
            print(f"  • Distancia: {meters_to_km(recent_run.get('distance', 0)):.2f} km")
            print(f"  • Tiempo: {seconds_to_time(recent_run.get('moving_time', 0))}")
            print(f"  • Desnivel: {recent_run.get('elevation_gain', 0):.0f} m")
            
            print("\n🏆 Total histórico:")
            print(f"  • Carreras: {all_run.get('count', 0)}")
            print(f"  • Distancia: {meters_to_km(all_run.get('distance', 0)):.2f} km")
            print(f"  • Tiempo: {seconds_to_time(all_run.get('moving_time', 0))}")
            
        except Exception as e:
            print(f"✗ Error al obtener estadísticas: {e}")
    
    def run(self):
        """Ejecuta el loop principal de la aplicación"""
        self.initialize()
        
        while True:
            self.show_menu()
            choice = input("\nSelecciona una opción: ").strip()
            
            if choice == '1':
                self.show_training_summary()
            elif choice == '2':
                self.get_coach_analysis()
            elif choice == '3':
                self.predict_race()
            elif choice == '4':
                self.suggest_workout()
            elif choice == '5':
                self.get_injury_prevention()
            elif choice == '6':
                self.chat_with_coach()
            elif choice == '7':
                self.calculate_training_paces()
            elif choice == '8':
                self.show_strava_stats()
            elif choice == '9':
                print("\n👋 ¡Nos vemos en el próximo entrenamiento!")
                break
            else:
                print("✗ Opción inválida")
            
            input("\nPresiona Enter para continuar...")


def main():
    """Función principal"""
    try:
        app = RunningCoachApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación interrumpida. ¡Hasta luego!")
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
