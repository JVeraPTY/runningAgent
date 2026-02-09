# CLAUDE.md

## Project Overview

RunningAgent is a Python CLI application that acts as an AI-powered running coach. It integrates Strava API data with the Anthropic Claude API to provide personalized training analysis, race predictions, workout suggestions, and injury prevention advice.

## Tech Stack

- **Language**: Python 3.8+
- **AI**: Anthropic Claude API (`claude-sonnet-4-20250514`)
- **External API**: Strava REST API with OAuth 2.0
- **Dependencies**: `anthropic>=0.39.0`, `requests>=2.31.0`
- **Package manager**: pip with `requirements.txt`

## Project Structure

All source files live in the project root (flat structure, no subdirectories):

- `main.py` — CLI entry point (`RunningCoachApp`), menu-driven interface
- `config.py` — Credentials (Strava, Claude), system prompt, analysis settings
- `strava_client.py` — `StravaAuth` (OAuth token mgmt) + `StravaClient` (activity fetching)
- `training_analyzer.py` — `TrainingAnalyzer`: metrics, weekly mileage, load analysis, risk detection
- `running_coach.py` — `RunningCoach` (Claude agent with conversation history) + `CoachTools` (pace/VDOT calculators)
- `example_usage.py` — Usage examples and demo scenarios
- `requirements.txt` — Python dependencies

## Architecture

Layered data flow: Strava API → `StravaClient` → `TrainingAnalyzer` → `RunningCoach` → CLI App

- **StravaClient**: OAuth 2.0 auth with **manual code entry** (for WSL compatibility), token persistence to `strava_token.json`, auto-refresh
- **TrainingAnalyzer**: Filters running activities, calculates metrics, generates context for LLM
- **RunningCoach**: Sends training context + user queries to Claude, maintains conversation history
- **CoachTools**: Jack Daniels paces, Riegel race prediction formula, VDOT estimation

### OAuth Flow

The authentication uses a **manual code entry approach**:
1. App displays authorization URL
2. User opens URL in browser and authorizes
3. User copies the redirect URL (or just the code parameter) from browser
4. User pastes it back in the terminal
5. App exchanges code for access token

This approach avoids HTTP server issues in WSL environments where localhost binding between Windows browser and WSL process doesn't work reliably.

## Known Issues & Solutions

### WSL OAuth Callback Issue

**Problem**: HTTP server on WSL cannot receive connections from Windows browser due to networking isolation.

**Solution**: Manual code entry flow - user copies redirect URL and pastes into terminal.

### Python External Environment Error

**Issue**: Modern Linux systems prevent global pip installs with `externally-managed-environment` error.

**Solution**: Always create and activate virtual environment before installing dependencies.

## Running the App

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/WSL

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

## Configuration

Credentials are loaded from `.env` file via `python-dotenv`:
- `STRAVA_CLIENT_ID` / `STRAVA_CLIENT_SECRET` — from https://www.strava.com/settings/api
- `STRAVA_REDIRECT_URI` — `http://localhost:8000/authorized`
- `CLAUDE_API_KEY` — from https://console.anthropic.com/
- `WEEKS_TO_ANALYZE` (default: 4), `MIN_ACTIVITIES_FOR_ANALYSIS` (default: 3)

Copy `.env.example` to `.env` and fill with real credentials.

## Key Conventions

- Primary language for UI text and comments is **Spanish**
- Code identifiers (class names, method names, variables) are in **English**
- Uses `.env` file for credentials (loaded via `python-dotenv`)
- `.gitignore` prevents committing sensitive files (`.env`, `strava_token.json`, `venv/`, `__pycache__/`)
- No testing framework is configured — no tests exist yet
- No linting or formatting tools are configured
- No database — all data is ephemeral; only OAuth tokens are cached locally
- **WSL compatible**: Manual OAuth flow works in Windows Subsystem for Linux

## Sensitive Files

- `.env` — contains real API credentials (never commit, already in `.gitignore`)
- `.env.example` — template file with placeholder values (safe to commit)
- `strava_token.json` — generated at runtime with OAuth tokens (in `.gitignore`)
- `venv/` — Python virtual environment (in `.gitignore`)
- `__pycache__/` — Python bytecode cache (in `.gitignore`)
