# 🏃 Running Coach Agent

Personal running coach powered by **Strava** + **Claude AI**

## 🎯 Features

- ✅ Automatic analysis of your Strava workouts
- ✅ Personalized advice based on your real data
- ✅ Race time predictions
- ✅ Specific workout suggestions
- ✅ Injury risk detection
- ✅ Training pace calculator
- ✅ Free chat with the coach for any questions

## 📋 Prerequisites

1. **Python 3.8+**
2. **Strava account** (with training data)
3. **Anthropic Claude API Key**
4. **Strava API Application**

## 🚀 Installation

### 1. Clone or download the project

```bash
cd running-coach-agent
```

### 2. Create virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows WSL/Linux
# or
venv\Scripts\activate    # On Windows CMD
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Strava API

1. Go to: https://www.strava.com/settings/api
2. Create a new application:
   - **Application Name**: Running Coach Agent
   - **Category**: Training
   - **Website**: http://localhost
   - **Authorization Callback Domain**: localhost

3. Copy your credentials:
   - `Client ID`
   - `Client Secret`

### 5. Configure Claude API

1. Go to: https://console.anthropic.com/
2. Generate an API Key in the "API Keys" section
3. Copy your API Key

### 6. Configure credentials (.env file)

IDs and secrets are not stored in code; they're loaded from a `.env` or `.env.dev` file that **is NOT uploaded to GitHub**.

1. Copy the template:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` (or `.env.dev`) and fill with your real credentials:

```bash
# Strava API - https://www.strava.com/settings/api
STRAVA_CLIENT_ID=12345
STRAVA_CLIENT_SECRET=abc123...
STRAVA_REDIRECT_URI=http://localhost:8000/authorized

# Claude API - https://console.anthropic.com/
CLAUDE_API_KEY=sk-ant-api...
```

## 🎮 Usage

### Run the application

```bash
# Activate virtual environment first (if using venv)
source venv/bin/activate  # Linux/WSL
# or venv\Scripts\activate  # Windows CMD

python main.py
```

### First time - Strava Authentication

1. **The application will display a URL** in the terminal
2. **Copy and paste the URL** into your browser
3. **Click "Authorize"** on the Strava page
4. **Copy the complete URL** from the address bar after redirection
   - The URL will look like: `http://localhost:8000/authorized?state=&code=XXXXX&scope=...`
   - Even if the browser shows an error, the URL contains the necessary code
5. **Paste the complete URL** (or just the code) in the terminal when prompted
6. The token will be saved in `strava_token.json` for future use

> 💡 **WSL Note**: If running from Windows Subsystem for Linux, the HTTP server won't work automatically. That's why we use the manual copy/paste method for the code.

### Main Menu

```
1. View training summary
2. Complete coach analysis
3. Predict race time
4. Suggest workout
5. Injury prevention tips
6. Ask the coach a question
7. Calculate training paces
8. View Strava statistics
9. Exit
```

## 💡 Usage Examples

### Training Analysis

The coach will automatically analyze:
- Weekly volume and trends
- Load progression (10% rule)
- Pace distribution
- Potential risks

### Race Prediction

Based on your recent workouts, predicts times for:
- 5K
- 10K
- Half Marathon
- Marathon

### Workout Suggestions

Generates detailed plans for:
- Intervals
- Tempo runs
- Long run
- Recovery
- Fartlek

### Free Chat

Ask anything about running:
- "How can I improve my 5K pace?"
- "Am I training too much?"
- "What strength exercises do you recommend?"

## 🏗️ Architecture

```
┌─────────────┐
│   Strava    │  ← Training data
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Training Analyzer │  ← Metrics analysis
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Running Coach   │  ← Agent with Claude
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│   Main App CLI   │  ← User interface
└──────────────────┘
```

## 📁 Project Structure

```
running-coach-agent/
├── main.py              # Main application
├── config.py            # Configuration (loads credentials from .env)
├── .env                 # Environment variables (DO NOT commit)
├── .env.example         # Variables template (copy to .env)
├── .gitignore          # Files to ignore in git
├── strava_client.py     # Strava API client
├── training_analyzer.py # Data analysis
├── running_coach.py     # Coach agent with Claude
├── requirements.txt     # Dependencies
├── README.md           # This documentation
├── CLAUDE.md           # Technical documentation
├── venv/               # Virtual environment (generated, DO NOT commit)
└── strava_token.json   # Strava token (generated, DO NOT commit)
```

## 🔧 Advanced Configuration

### Change analysis period

In `.env` (or `.env.dev`):

```python
WEEKS_TO_ANALYZE = 8  # Analyze last 8 weeks
```

### Customize coach prompt

Edit `COACH_SYSTEM_PROMPT` in `config.py` to adjust the coach's personality and focus.

### Use different Claude models

In `running_coach.py`:

```python
self.model = "claude-opus-4-20250514"  # For deeper analysis
```

## 🛠️ Troubleshooting

### Error: "Authorization code not received"

- Make sure to copy the complete URL after clicking "Authorize"
- If only copying the code, it must be the full value after `code=`
- Verify that `STRAVA_REDIRECT_URI` in `.env` is exactly `http://localhost:8000/authorized`

### Error: "Token expired"

- The token refreshes automatically
- If it persists, delete `strava_token.json` and re-authenticate

### Activities not loading

- Verify you have running activities in Strava
- Increase `WEEKS_TO_ANALYZE` if your workouts are older

### Running in WSL (Windows Subsystem for Linux)

- Authentication flow uses manual code entry (not HTTP server)
- Make sure to activate the virtual environment before running
- Generated files (`.env`, `strava_token.json`) are created in the WSL system

### Error: "externally-managed-environment"

This error occurs on modern Linux systems when trying to install packages globally:

```bash
# Solution: use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🔐 Security

- **NEVER** upload the `.env` or `.env.dev` file (already in `.gitignore`)
- Don't share credentials; use `.env.example` as template without real values
- Credentials are only used locally

## 🤝 Contributions

Ideas for improvements:
- Web interface with Streamlit
- Progress charts
- Integration with more platforms (Garmin, Polar)
- Export training plans
- Automatic notifications

## 📝 License

Personal project - Free use

## 🙏 Acknowledgements

- **Strava API** for access to training data
- **Anthropic Claude** for the LLM power
- **Jack Daniels** for training formulas

---

Made with ❤️ for data-loving runners

Questions? Contact [your email]
