# 🏃 Running Coach Agent

Coach de running personal powered by **Strava** + **Claude AI**

## 🎯 Características

- ✅ Análisis automático de tus entrenamientos de Strava
- ✅ Consejos personalizados basados en tus datos reales
- ✅ Predicción de tiempos de carrera
- ✅ Sugerencias de entrenamientos específicos
- ✅ Detección de riesgos de lesión
- ✅ Calculadora de paces de entrenamiento
- ✅ Chat libre con el coach para cualquier duda

## 📋 Requisitos Previos

1. **Python 3.8+**
2. **Cuenta de Strava** (con datos de entrenamiento)
3. **API Key de Anthropic Claude**
4. **Strava API Application**

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd running-coach-agent
```

### 2. Crear entorno virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows WSL/Linux
# o
venv\Scripts\activate    # En Windows CMD
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Strava API

1. Ve a: https://www.strava.com/settings/api
2. Crea una nueva aplicación:
   - **Application Name**: Running Coach Agent
   - **Category**: Training
   - **Website**: http://localhost
   - **Authorization Callback Domain**: localhost

3. Copia tus credenciales:
   - `Client ID`
   - `Client Secret`

### 5. Configurar Claude API

1. Ve a: https://console.anthropic.com/
2. Genera una API Key en la sección "API Keys"
3. Copia tu API Key

### 6. Configurar credenciales (archivo .env)

Los IDs y secretos no van en el código; se cargan desde un archivo `.env` o `.env.dev` que **no se sube a GitHub**.

1. Copia la plantilla:
   ```bash
   cp .env.example .env
   ```
2. Edita `.env` (o `.env.dev`) y rellena con tus credenciales reales:

```bash
# Strava API - https://www.strava.com/settings/api
STRAVA_CLIENT_ID=12345
STRAVA_CLIENT_SECRET=abc123...
STRAVA_REDIRECT_URI=http://localhost:8000/authorized

# Claude API - https://console.anthropic.com/
CLAUDE_API_KEY=sk-ant-api...
```

## 🎮 Uso

### Ejecutar la aplicación

```bash
# Activa el entorno virtual primero (si usas venv)
source venv/bin/activate  # Linux/WSL
# o venv\Scripts\activate  # Windows CMD

python main.py
```

### Primera vez - Autenticación con Strava

1. **La aplicación mostrará una URL** en la terminal
2. **Copia y pega la URL** en tu navegador
3. **Haz clic en "Authorize"** en la página de Strava
4. **Copia la URL completa** de la barra de direcciones después de la redirección
   - La URL se verá así: `http://localhost:8000/authorized?state=&code=XXXXX&scope=...`
   - Aunque el navegador muestre error, la URL contiene el código necesario
5. **Pega la URL completa** (o solo el código) en la terminal cuando se te pida
6. El token se guardará en `strava_token.json` para futuros usos

> 💡 **Nota WSL**: Si ejecutas desde Windows Subsystem for Linux, el servidor HTTP no funcionará automáticamente. Por eso usamos el método manual de copiar/pegar el código.

### Menú Principal

```
1. Ver resumen de entrenamiento
2. Análisis completo del coach
3. Predecir tiempo de carrera
4. Sugerir entrenamiento
5. Consejos de prevención de lesiones
6. Hacer pregunta al coach
7. Calcular paces de entrenamiento
8. Ver estadísticas de Strava
9. Salir
```

## 💡 Ejemplos de Uso

### Análisis de Entrenamiento

El coach analizará automáticamente:
- Volumen semanal y tendencias
- Progresión de carga (regla del 10%)
- Distribución de paces
- Riesgos potenciales

### Predicción de Carrera

Basándose en tus entrenamientos recientes, predice tiempos para:
- 5K
- 10K
- Media Maratón
- Maratón

### Sugerencias de Entrenamientos

Genera planes detallados para:
- Intervalos
- Tempo runs
- Carrera larga
- Recuperación
- Fartlek

### Chat Libre

Pregunta cualquier cosa sobre running:
- "¿Cómo mejoro mi pace en 5K?"
- "¿Estoy entrenando demasiado?"
- "¿Qué ejercicios de fuerza me recomiendas?"

## 🏗️ Arquitectura

```
┌─────────────┐
│   Strava    │  ← Datos de entrenamientos
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Training Analyzer │  ← Análisis de métricas
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Running Coach   │  ← Agente con Claude
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│   Main App CLI   │  ← Interfaz de usuario
└──────────────────┘
```

## 📁 Estructura del Proyecto

```
running-coach-agent/
├── main.py              # Aplicación principal
├── config.py            # Configuración (carga credenciales desde .env)
├── .env                 # Variables de entorno (NO commitear)
├── .env.example         # Plantilla de variables (copiar a .env)
├── .gitignore          # Archivos a ignorar en git
├── strava_client.py     # Cliente de Strava API  
├── training_analyzer.py # Análisis de datos
├── running_coach.py     # Agente coach con Claude
├── requirements.txt     # Dependencias
├── README.md           # Esta documentación
├── CLAUDE.md           # Documentación técnica
├── venv/               # Entorno virtual (generado, NO commitear)
└── strava_token.json   # Token de Strava (generado, NO commitear)
```

## 🔧 Configuración Avanzada

### Cambiar el periodo de análisis

En `.env` (o `.env.dev`):

```python
WEEKS_TO_ANALYZE = 8  # Analizar últimas 8 semanas
```

### Personalizar el prompt del coach

Edita `COACH_SYSTEM_PROMPT` en `config.py` para ajustar la personalidad y enfoque del coach.

### Usar diferentes modelos de Claude

En `running_coach.py`:

```python
self.model = "claude-opus-4-20250514"  # Para análisis más profundos
```

## 🛠️ Solución de Problemas

### Error: "No se recibió el código de autorización"

- Asegúrate de copiar la URL completa después de hacer clic en "Authorize"
- Si solo copias el código, debe ser el valor completo después de `code=`
- Verifica que el `STRAVA_REDIRECT_URI` en `.env` sea exactamente `http://localhost:8000/authorized`

### Error: "Token expirado"

- El token se refresca automáticamente
- Si persiste, elimina `strava_token.json` y vuelve a autenticar

### No se cargan actividades

- Verifica que tengas actividades de running en Strava
- Aumenta `WEEKS_TO_ANALYZE` si tus entrenamientos son más antiguos

### Ejecutando en WSL (Windows Subsystem for Linux)

- El flujo de autenticación usa entrada manual del código (no servidor HTTP)
- Asegúrate de tener el entorno virtual activado antes de ejecutar
- Los archivos generados (`.env`, `strava_token.json`) se crean en el sistema WSL

### Error: "externally-managed-environment"

Este error ocurre en sistemas Linux modernos cuando intentas instalar paquetes globalmente:

```bash
# Solución: usar entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🔐 Seguridad

- **NUNCA** subas el archivo `.env` o `.env.dev` (ya están en `.gitignore`)
- No compartas credenciales; usa `.env.example` como plantilla sin valores reales
- Las credenciales solo se usan localmente

## 🤝 Contribuciones

Ideas para mejoras:
- Interfaz web con Streamlit
- Gráficas de progreso
- Integración con más plataformas (Garmin, Polar)
- Exportar planes de entrenamiento
- Notificaciones automáticas

## 📝 Licencia

Proyecto personal - Uso libre

## 🙏 Agradecimientos

- **Strava API** por el acceso a datos de entrenamiento
- **Anthropic Claude** por el poder del LLM
- **Jack Daniels** por las fórmulas de entrenamiento

---

Hecho con ❤️ para corredores que aman los datos

¿Preguntas? Contacta a [tu email]
