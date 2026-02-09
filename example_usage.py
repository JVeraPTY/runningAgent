#!/usr/bin/env python3
"""
Ejemplo de uso del Running Coach Agent sin interfaz CLI
Útil para integración en otros proyectos o automatización
"""

from datetime import datetime, timedelta
from config import (
    STRAVA_CLIENT_ID,
    STRAVA_CLIENT_SECRET,
    STRAVA_REDIRECT_URI,
    CLAUDE_API_KEY,
    COACH_SYSTEM_PROMPT
)
from strava_client import authenticate_strava, StravaClient
from training_analyzer import TrainingAnalyzer
from running_coach import RunningCoach, CoachTools


def example_basic_usage():
    """Ejemplo básico de uso del agente"""
    
    print("=== EJEMPLO 1: Uso Básico ===\n")
    
    # 1. Autenticar con Strava
    auth = authenticate_strava(
        STRAVA_CLIENT_ID,
        STRAVA_CLIENT_SECRET,
        STRAVA_REDIRECT_URI
    )
    client = StravaClient(auth)
    
    # 2. Obtener actividades
    after_date = datetime.now() - timedelta(weeks=4)
    activities = client.get_activities(after=after_date)
    
    # 3. Analizar datos
    analyzer = TrainingAnalyzer(activities)
    
    # 4. Crear coach
    coach = RunningCoach(CLAUDE_API_KEY, COACH_SYSTEM_PROMPT)
    coach.set_training_context(analyzer)
    
    # 5. Obtener análisis
    analysis = coach.analyze_training()
    print(analysis)


def example_specific_questions():
    """Ejemplo de preguntas específicas al coach"""
    
    print("\n=== EJEMPLO 2: Preguntas Específicas ===\n")
    
    # Setup inicial
    auth = authenticate_strava(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REDIRECT_URI)
    client = StravaClient(auth)
    activities = client.get_activities(after=datetime.now() - timedelta(weeks=4))
    analyzer = TrainingAnalyzer(activities)
    coach = RunningCoach(CLAUDE_API_KEY, COACH_SYSTEM_PROMPT)
    coach.set_training_context(analyzer)
    
    # Hacer diferentes preguntas
    questions = [
        "¿Estoy listo para correr un medio maratón?",
        "¿Qué puedo hacer para mejorar mi pace?",
        "Dame un plan de entrenamiento para la próxima semana"
    ]
    
    for question in questions:
        print(f"\nPregunta: {question}")
        print("-" * 60)
        response = coach.ask(question)
        print(response)
        print()


def example_calculate_paces():
    """Ejemplo de cálculo de paces sin necesidad de Strava"""
    
    print("\n=== EJEMPLO 3: Calcular Paces ===\n")
    
    # Basado en un 5K en 22 minutos
    paces = CoachTools.calculate_training_paces(22.0)
    
    print("Paces de entrenamiento para un 5K de 22:00:")
    print(f"  Easy/Recuperación: {paces['easy']}")
    print(f"  Long Run: {paces['long_run']}")
    print(f"  Tempo: {paces['tempo']}")
    print(f"  Intervalos: {paces['interval']}")
    print(f"  Repeticiones: {paces['repetition']}")


def example_race_prediction():
    """Ejemplo de predicción de tiempos de carrera"""
    
    print("\n=== EJEMPLO 4: Predicción de Carreras ===\n")
    
    # Basado en un 5K reciente
    recent_5k_minutes = 22.0
    
    # Estimar tiempos para diferentes distancias
    distances = [
        (10, "10K"),
        (21.0975, "Media Maratón"),
        (42.195, "Maratón")
    ]
    
    for distance_km, name in distances:
        estimated_time = CoachTools.estimate_race_time(
            distance_km=distance_km,
            reference_distance_km=5,
            reference_time_minutes=recent_5k_minutes
        )
        
        hours = int(estimated_time // 60)
        minutes = int(estimated_time % 60)
        
        print(f"{name} ({distance_km} km):")
        if hours > 0:
            print(f"  Tiempo estimado: {hours}h {minutes:02d}min")
        else:
            print(f"  Tiempo estimado: {minutes}min")
        print()


def example_programmatic_analysis():
    """Ejemplo de análisis programático de datos"""
    
    print("\n=== EJEMPLO 5: Análisis Programático ===\n")
    
    # Setup
    auth = authenticate_strava(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REDIRECT_URI)
    client = StravaClient(auth)
    activities = client.get_activities(after=datetime.now() - timedelta(weeks=4))
    analyzer = TrainingAnalyzer(activities)
    
    # Obtener métricas específicas
    summary = analyzer.get_summary_stats()
    weekly = analyzer.get_weekly_mileage()
    load = analyzer.analyze_training_load()
    issues = analyzer.detect_potential_issues()
    
    print("Resumen:")
    print(f"  Total carreras: {summary['total_runs']}")
    print(f"  Distancia total: {summary['total_distance_km']} km")
    print(f"  Pace promedio: {summary['avg_pace']}")
    
    print(f"\nSemana actual: {weekly[0]['distance_km']} km")
    print(f"Cambio de volumen: {load['load_change_percent']}%")
    
    print("\nProblemas detectados:")
    for issue in issues:
        print(f"  - {issue}")


def example_full_workflow():
    """Ejemplo de workflow completo: cargar datos, analizar y obtener recomendaciones"""
    
    print("\n=== EJEMPLO 6: Workflow Completo ===\n")
    
    # 1. Conectar con Strava
    print("1. Conectando con Strava...")
    auth = authenticate_strava(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REDIRECT_URI)
    client = StravaClient(auth)
    athlete = client.get_athlete()
    print(f"   Atleta: {athlete['firstname']} {athlete['lastname']}")
    
    # 2. Cargar datos
    print("\n2. Cargando actividades...")
    activities = client.get_activities(after=datetime.now() - timedelta(weeks=6))
    print(f"   Actividades cargadas: {len(activities)}")
    
    # 3. Analizar
    print("\n3. Analizando datos...")
    analyzer = TrainingAnalyzer(activities)
    summary = analyzer.get_summary_stats()
    print(f"   Carreras: {summary['total_runs']}")
    print(f"   Km totales: {summary['total_distance_km']}")
    
    # 4. Crear coach
    print("\n4. Inicializando coach...")
    coach = RunningCoach(CLAUDE_API_KEY, COACH_SYSTEM_PROMPT)
    coach.set_training_context(analyzer)
    
    # 5. Obtener recomendaciones
    print("\n5. Generando recomendaciones...\n")
    print("-" * 60)
    
    recommendation = coach.ask(
        "Dame 3 recomendaciones concretas para mejorar mi entrenamiento esta semana"
    )
    print(recommendation)


if __name__ == "__main__":
    """
    Descomenta el ejemplo que quieras ejecutar
    """
    
    # Ejemplo básico
    # example_basic_usage()
    
    # Preguntas específicas
    # example_specific_questions()
    
    # Cálculo de paces (no requiere Strava)
    example_calculate_paces()
    
    # Predicción de carreras (no requiere Strava)
    example_race_prediction()
    
    # Análisis programático
    # example_programmatic_analysis()
    
    # Workflow completo
    # example_full_workflow()
