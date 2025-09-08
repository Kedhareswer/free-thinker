# 🧠 FreeThinker
> **Your intelligent, reasoning AI agent with free search capabilities**

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-UI-ff7c00?style=for-the-badge&logo=gradio&logoColor=white)](https://gradio.app)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=for-the-badge)](https://github.com/Kedhareswer/free-thinker/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Kedhareswer-181717?style=for-the-badge&logo=github)](https://github.com/Kedhareswer/free-thinker)

*An AI agent that **reasons**, **verifies sources**, and works with **free search engines** (no API keys required!)*

[🚀 Quick Start](#-quick-start) • [🛠️ Features](#-features) • [📊 Visualizations](#-visualizations) • [🔧 Setup](#-setup)

</div>

---

## 🌟 What Makes FreeThinker Special?

🧠 **Reasoning Agent** - Verifies sources and double-checks information  
🆓 **Free Search** - Uses DuckDuckGo & Bing when no API keys provided  
🎨 **Rich UI** - Interactive tables, charts, and maps  
⚡ **Multi-Provider** - Groq, Gemini, Mistral support  
🔄 **Live Refresh** - Fetch latest models from providers  

---

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/Kedhareswer/free-thinker.git
cd free-thinker
pip install -r requirements.txt

# Launch UI
python app.py
```

**No API keys?** No problem! FreeThinker works with free search engines out of the box.

---

## 🛠️ Features

### 🔍 Smart Search System
| Search Engine | Type | API Key Required |
|---|---|---|
| 🔥 **Google** (via Serper) | Premium | ✅ Optional |
| 🦆 **DuckDuckGo** | Free | ❌ No |
| 🌐 **Bing** | Free | ❌ No |

### 🤖 AI Providers
| Provider | Models | Get API Key |
|---|---|---|
| ⚡ **Groq** | `llama-3.1-70b-versatile`, `llama-3.1-8b-instant` | [console.groq.com](https://console.groq.com/keys) |
| 🤖 **Gemini** | `gemini-1.5-pro`, `gemini-1.5-flash` | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| 🦙 **Mistral** | `mistral-large-latest`, `open-mistral-7b` | [console.mistral.ai](https://console.mistral.ai/api-keys/) |

### 🛠️ Tools Available
- 🔍 **Smart Search** - Google/DuckDuckGo/Bing with source verification
- 🌤️ **Weather** - OpenWeatherMap with maps
- 📱 **Reddit** - Subreddit scraping with score analysis  
- 🌐 **Web Scraper** - Extract content from any webpage
- 🧮 **Calculator** - Basic math operations

---

## 📊 Visualizations

The UI automatically generates:

| Output Type | Example | When |
|---|---|---|
| 📊 **Charts** | Weather metrics, Reddit scores | Weather/Reddit queries |
| 🗺️ **Maps** | City location with marker | Weather queries |
| 📋 **Tables** | Reddit posts with Title/Score/Body | Reddit queries |

---

## 🔧 Setup

### 1️⃣ Environment
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# Linux/Mac  
source .venv/bin/activate
```

### 2️⃣ Install
```bash
pip install -r requirements.txt
```

### 3️⃣ Run
```bash
# Web UI (recommended)
python app.py

# CLI mode
python -m agent
```

---

## 🎯 Usage Examples

### 💬 In the UI:
1. **Select Provider**: Groq, Gemini, or Mistral
2. **Enter API Key**: Or leave empty to use free search
3. **Ask Questions**: 
   - *"What's the weather in Tokyo?"*
   - *"Search for recent AI developments"*  
   - *"Get top 5 posts from r/Python"*

### 🧠 Reasoning Features:
- ✅ **Source Verification** for search results
- 🔍 **Consistency Checking** across multiple sources  
- 📊 **Confidence Scoring** for information reliability
- 🔄 **Cross-validation** suggestions

---

## 📁 Project Structure

```
free-thinker/
├── 🎨 app.py                 # Gradio UI
├── 🧠 agent.py               # Reasoning agent core
├── 🤖 models/                # AI provider integrations
├── 🛠️ tools/                 # Tool implementations  
├── 💬 prompts/               # System & format prompts
├── ⚙️ config/                # Configuration files
└── 📄 requirements.txt       # Dependencies
```

---

## 🔐 API Keys (Optional)

Add to UI or `config/.env`:

```env
# AI Providers (choose one)
GROQ_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here  
MISTRAL_API_KEY=your_key_here

# Tools (all optional - free alternatives available)
SERPER_API_KEY=your_key_here     # Google search
WEATHER_API_KEY=your_key_here    # Weather data
CLIENT_ID=your_key_here          # Reddit  
CLIENT_SECRET=your_key_here      # Reddit
```

---

## 🤝 Contributing

Found a bug? Want to add a feature? PRs welcome!

1. Fork the repo
2. Create your feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

Apache 2.0 License - see [LICENSE](https://github.com/Kedhareswer/free-thinker/blob/main/LICENSE)

---

<div align="center">

**Made with ❤️ for the AI community**

⭐ Star this repo if you find it useful!

</div>
