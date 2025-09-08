# FreeThinker: Your own free of charge AI agent

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Gradio](https://img.shields.io/badge/Gradio-UI-brightgreen)
![License](https://img.shields.io/badge/License-Apache_2.0-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)
![Type](https://img.shields.io/badge/Type-Agent-orange)

FreeThinker is an AI agent that uses no-cost/open APIs to automate tasks through natural language. It supports multiple providers (Groq, Gemini, Mistral) and includes a modern Gradio UI with structured outputs: tables, charts, and maps.

---

## Table of Contents
1. Overview
2. Features
3. Providers and Models
4. API Keys
5. Project Structure
6. Installation
7. Configuration
8. Usage
9. Visualizations (Tables, Charts, Maps)
10. Prompts
11. Development Notes
12. Git Quickstart (init and push)
13. License
14. Contact

---

## 1) Overview
FreeThinker automates tasks via natural language. It selects the right tool for each prompt and uses your chosen LLM provider and model. The UI shows raw output, tables, charts, and maps.

## 2) Features
- No-cost API usage (where available).
- Multiple providers: Groq, Gemini, Mistral (official).
- Tools: Search (Serper), Weather (OpenWeather), Reddit scraping, Web scraping, Basic calculator.
- Gradio UI with:
  - Raw output,
  - Tables,
  - Plotly charts,
  - Folium maps,
  - Live model refresh,
  - Runtime API key inputs,
  - Prompts preview (system + format prompts).

## 3) Providers and Models (examples)
| Provider | Example Models |
|---|---|
| Groq | `llama-3.1-70b-versatile`, `llama-3.1-8b-instant` |
| Gemini | `gemini-1.5-pro`, `gemini-1.5-flash` |
| Mistral (official) | `mistral-large-latest`, `open-mistral-7b`, `open-mixtral-8x7b`, `codestral-latest` |

Use the “Refresh Models” button in the UI to fetch the latest model list from the selected provider (after entering the provider key).

## 4) API Keys
| Purpose | Key Name | Where to get it |
|---|---|---|
| Groq models | `GROQ_API_KEY` | https://console.groq.com/keys |
| Gemini models | `GOOGLE_API_KEY` | https://aistudio.google.com/app/apikey |
| Mistral models | `MISTRAL_API_KEY` | https://console.mistral.ai/api-keys/ |
| Web search (Serper) | `SERPER_API_KEY` | https://serper.dev |
| Weather (OpenWeather) | `WEATHER_API_KEY` | https://openweathermap.org/api |
| Reddit tool | `CLIENT_ID`, `CLIENT_SECRET` | https://www.reddit.com/prefs/apps |

Keys entered in the UI override `.env` for the current session.

## 5) Project Structure
```
FreeThinker/
├─ app.py                  # Gradio UI
├─ agent.py                # Core agent orchestration
├─ models/
│  ├─ llama_3_1_70B.py     # Groq provider
│  ├─ gemini.py            # Gemini provider
│  └─ mistral.py           # Mistral (official) provider
├─ tools/
│  ├─ search_tool.py       # Google (Serper) search
│  ├─ weather_forecaster.py# OpenWeather
│  ├─ reddit_scrapper.py   # Reddit scraping
│  ├─ scrape_tool.py       # Simple web scraper
│  └─ basic_calculator.py  # Calculator
├─ prompts/
│  ├─ system_prompt.py     # System prompt template
│  └─ format_prompt.py     # Format prompts per tool
├─ config/
│  └─ .env                 # Optional fallback for keys
├─ requirements.txt
├─ .gitignore
└─ README.md
```

## 6) Installation
```bash
# Optional but recommended: virtual environment
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Install dependencies
pip install -r requirements.txt
```

## 7) Configuration
You can add keys in `config/.env` (optional fallback):
```
GROQ_API_KEY=...
GOOGLE_API_KEY=...
MISTRAL_API_KEY=...
SERPER_API_KEY=...
WEATHER_API_KEY=...
CLIENT_ID=...
CLIENT_SECRET=...
```
In the UI, you can enter these keys at runtime (they take precedence over .env).

## 8) Usage

### CLI (terminal)
```bash
python -m agent
```
Type `exit` to quit.

### Gradio App (web UI)
```bash
python app.py
```
This opens a local Gradio interface: http://127.0.0.1:7860

- Enter a prompt and select provider/model.
- Paste your API keys in the UI.
- Click “Refresh Models” after entering the provider key to fetch the latest models.

## 9) Visualizations (Tables, Charts, Maps)

- Tables:
  - Reddit results parsed into a table with columns `Title`, `Score`, `Body`.
- Charts:
  - Weather: bar chart of `Temperature`, `Feels like`, `Min`, `Max`.
  - Reddit: bar chart of `Score` by `Title`.
- Maps:
  - Weather: Folium map of the city (geocoded using OSM Nominatim).

Optional placeholders for screenshots:
- UI Overview: `docs/images/ui-overview.png`
- Reddit Table + Chart: `docs/images/reddit-table-chart.png`
- Weather Chart + Map: `docs/images/weather-chart-map.png`

## 10) Prompts
- The “Prompts (System and Format)” accordion in the UI shows:
  - The active system prompt (from `prompts/system_prompt.py`) with live tool descriptions.
  - The format prompt per tool (from `prompts/format_prompt.py`).

## 11) Development Notes
- The agent returns a structured dict for UI rendering while preserving CLI prints.
- Tools and providers accept runtime keys and fall back to `.env` / environment variables.
- Error handling is defensive and returns user-friendly messages.

## 12) Git Quickstart (init and push)
Caution: the first step deletes local Git history.

Linux/macOS:
```bash
rm -rf .git
git init
git remote add origin https://github.com/Kedhareswer/free-thinker.git
git add .
git branch -M main
git commit -m "chore: init repo with Gradio UI, providers, docs, and .gitignore"
git push -u origin main
```

Windows PowerShell (first command only differs):
```powershell
Remove-Item -Recurse -Force .git
git init
git remote add origin https://github.com/Kedhareswer/free-thinker.git
git add .
git branch -M main
git commit -m "chore: init repo with Gradio UI, providers, docs, and .gitignore"
git push -u origin main
```

## 13) License
This project is licensed under the Apache 2.0 License. See the LICENSE file.

## 14) Contact
- Email: diegovelillarecio@gmail.com
- GitHub: https://github.com/diegovelilla
- Hugging Face: https://huggingface.co/diegovelilla
- LinkedIn: https://www.linkedin.com/in/diego-velilla-recio/
