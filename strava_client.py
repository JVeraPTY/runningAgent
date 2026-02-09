"""
Módulo para interactuar con la API de Strava
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import socket
import time


class StravaAuth:
    """Maneja la autenticación OAuth con Strava"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        
    def get_authorization_url(self) -> str:
        """Genera la URL de autorización de Strava"""
        scope = "read,activity:read_all"
        auth_url = (
            f"https://www.strava.com/oauth/authorize?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}"
        )
        return auth_url
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Intercambia el código de autorización por un token de acceso"""
        token_url = "https://www.strava.com/oauth/token"
        
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        self.refresh_token = token_data['refresh_token']
        self.expires_at = token_data['expires_at']
        
        return token_data
    
    def save_token(self, filename: str = 'strava_token.json'):
        """Guarda el token en un archivo"""
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at
        }
        with open(filename, 'w') as f:
            json.dump(token_data, f)
    
    def load_token(self, filename: str = 'strava_token.json') -> bool:
        """Carga el token desde un archivo"""
        try:
            with open(filename, 'r') as f:
                token_data = json.load(f)
                self.access_token = token_data['access_token']
                self.refresh_token = token_data['refresh_token']
                self.expires_at = token_data['expires_at']
                return True
        except FileNotFoundError:
            return False
    
    def is_token_valid(self) -> bool:
        """Verifica si el token actual es válido"""
        if not self.access_token or not self.expires_at:
            return False
        return datetime.now().timestamp() < self.expires_at
    
    def refresh_access_token(self):
        """Refresca el token de acceso usando el refresh token"""
        token_url = "https://www.strava.com/oauth/token"
        
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        self.refresh_token = token_data['refresh_token']
        self.expires_at = token_data['expires_at']
        
        self.save_token()


class AuthCallbackHandler(BaseHTTPRequestHandler):
    """Handler para capturar el callback de OAuth"""
    
    authorization_code = None
    
    def do_GET(self):
        try:
            print(f"\n📥 Solicitud recibida: {self.path}")
            query_components = parse_qs(urlparse(self.path).query)
            
            if 'code' in query_components:
                AuthCallbackHandler.authorization_code = query_components['code'][0]
                
                # Preparar respuesta HTML simple y corta
                html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Autenticacion Exitosa</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        h1 { margin: 0 0 20px 0; font-size: 2.5em; }
        p { font-size: 1.2em; margin: 10px 0; }
        .checkmark { font-size: 4em; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="checkmark">&#10003;</div>
        <h1>Autenticacion Completada!</h1>
        <p>Ya puedes cerrar esta ventana</p>
        <p>Vuelve a la terminal para continuar</p>
    </div>
</body>
</html>"""
                
                # Enviar respuesta HTTP correctamente formada
                html_bytes = html_content.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html_bytes)))
                self.send_header('Connection', 'close')
                self.end_headers()
                self.wfile.write(html_bytes)
                
                print("\n✓ Código de autorización recibido")
            else:
                # Error: no se recibió código
                error_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Error</title>
</head>
<body>
    <h1>Error: No se recibio el codigo de autorizacion</h1>
    <p>Por favor, intenta de nuevo.</p>
</body>
</html>"""
                error_bytes = error_html.encode('utf-8')
                self.send_response(400)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(error_bytes)))
                self.send_header('Connection', 'close')
                self.end_headers()
                self.wfile.write(error_bytes)
        except Exception as e:
            print(f"\n⚠ Error procesando callback: {e}")
            try:
                simple_error = b"Error procesando la solicitud"
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', str(len(simple_error)))
                self.send_header('Connection', 'close')
                self.end_headers()
                self.wfile.write(simple_error)
            except:
                pass
    
    def log_message(self, format, *args):
        # Silenciar logs del servidor
        pass


class StravaClient:
    """Cliente para interactuar con la API de Strava"""
    
    def __init__(self, auth: StravaAuth):
        self.auth = auth
        self.base_url = "https://www.strava.com/api/v3"
    
    def _ensure_valid_token(self):
        """Asegura que el token sea válido antes de hacer requests"""
        if not self.auth.is_token_valid():
            self.auth.refresh_access_token()
    
    def _get_headers(self) -> Dict:
        """Retorna los headers para las peticiones"""
        return {'Authorization': f'Bearer {self.auth.access_token}'}
    
    def get_athlete(self) -> Dict:
        """Obtiene información del atleta"""
        self._ensure_valid_token()
        response = requests.get(
            f"{self.base_url}/athlete",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_activities(
        self, 
        after: Optional[datetime] = None,
        before: Optional[datetime] = None,
        per_page: int = 30
    ) -> List[Dict]:
        """
        Obtiene actividades del atleta
        
        Args:
            after: Fecha desde la cual obtener actividades
            before: Fecha hasta la cual obtener actividades
            per_page: Número de actividades por página
        """
        self._ensure_valid_token()
        
        params = {'per_page': per_page}
        
        if after:
            params['after'] = int(after.timestamp())
        if before:
            params['before'] = int(before.timestamp())
        
        activities = []
        page = 1
        
        while True:
            params['page'] = page
            response = requests.get(
                f"{self.base_url}/athlete/activities",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            
            page_activities = response.json()
            if not page_activities:
                break
                
            activities.extend(page_activities)
            page += 1
            
            # Límite de seguridad
            if page > 10:
                break
        
        return activities
    
    def get_activity_details(self, activity_id: int) -> Dict:
        """Obtiene detalles completos de una actividad específica"""
        self._ensure_valid_token()
        response = requests.get(
            f"{self.base_url}/activities/{activity_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_activity_stats(self) -> Dict:
        """Obtiene estadísticas agregadas del atleta"""
        self._ensure_valid_token()
        athlete = self.get_athlete()
        athlete_id = athlete['id']
        
        response = requests.get(
            f"{self.base_url}/athletes/{athlete_id}/stats",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()


def authenticate_strava(client_id: str, client_secret: str, redirect_uri: str) -> StravaAuth:
    """
    Proceso completo de autenticación con Strava
    
    Returns:
        StravaAuth: Objeto de autenticación con tokens válidos
    """
    auth = StravaAuth(client_id, client_secret, redirect_uri)
    
    # Intentar cargar token existente
    if auth.load_token():
        if auth.is_token_valid():
            print("✓ Token cargado exitosamente")
            return auth
        else:
            print("⟳ Token expirado, refrescando...")
            auth.refresh_access_token()
            return auth
    
    # Si no hay token, iniciar flujo OAuth
    print("\n" + "=" * 70)
    print("🔐 INICIANDO AUTENTICACIÓN CON STRAVA")
    print("=" * 70)
    
    # Generar URL de autorización
    auth_url = auth.get_authorization_url()
    
    # Mostrar URL de forma destacada
    print("\n📋 PASO 1: COPIA Y PEGA ESTA URL EN TU NAVEGADOR:\n")
    print("─" * 70)
    print(auth_url)
    print("─" * 70)
    
    # Intentar abrir navegador automáticamente (puede fallar en WSL)
    try:
        webbrowser.open(auth_url)
        print("\n✓ Se intentó abrir el navegador automáticamente")
    except Exception as e:
        pass
    
    print("\n📋 PASO 2: Después de hacer clic en 'Authorize':")
    print("   - Serás redirigido a una URL que empieza con:")
    print("     http://localhost:8000/authorized?...")
    print("   - Copia la URL COMPLETA de la barra de direcciones")
    print("   - Busca el parámetro 'code=' en la URL\n")
    
    print("📋 PASO 3: Pega la URL completa o solo el código aquí:\n")
    
    # Pedir al usuario que ingrese el código manualmente
    redirect_response = input("URL completa o código de autorización: ").strip()
    
    # Extraer el código de la URL si el usuario pegó la URL completa
    if redirect_response.startswith('http'):
        parsed = urlparse(redirect_response)
        query_params = parse_qs(parsed.query)
        if 'code' in query_params:
            authorization_code = query_params['code'][0]
        else:
            raise Exception("No se encontró el código en la URL proporcionada")
    else:
        # Asumir que el usuario pegó solo el código
        authorization_code = redirect_response
    
    if not authorization_code:
        raise Exception("No se recibió el código de autorización")
    
    # Intercambiar código por token
    print("\n🔄 Intercambiando código por token de acceso...")
    auth.exchange_code_for_token(authorization_code)
    auth.save_token()
    
    print("\n" + "=" * 70)
    print("✅ AUTENTICACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("✓ Token guardado en strava_token.json")
    print("✓ Ya puedes usar el agente de coach\n")
    return auth


def meters_to_km(meters: float) -> float:
    """Convierte metros a kilómetros"""
    return meters / 1000


def seconds_to_time(seconds: int) -> str:
    """Convierte segundos a formato HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    else:
        return f"{minutes}m {secs:02d}s"


def calculate_pace(distance_meters: float, time_seconds: int) -> str:
    """
    Calcula el pace en min/km
    
    Returns:
        str: Pace en formato "MM:SS /km"
    """
    if distance_meters == 0:
        return "N/A"
    
    km = meters_to_km(distance_meters)
    pace_seconds = time_seconds / km
    
    minutes = int(pace_seconds // 60)
    seconds = int(pace_seconds % 60)
    
    return f"{minutes}:{seconds:02d} /km"
