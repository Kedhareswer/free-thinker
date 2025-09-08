import re
import json
from typing import Tuple, Optional, Dict, List

import gradio as gr
import pandas as pd
import plotly.express as px
import folium
from folium import Map, Marker
import requests
import os

from agent import Agent
from tools.basic_calculator import basic_calculator
from tools.weather_forecaster import weather_forecaster
from tools.reddit_scrapper import reddit_scrapper
from tools.scrape_tool import scrape_tool
from tools.search_tool import search_tool
from models.llama_3_1_70B import llama_3_1_70B
from models.mistral import mistral_model
from models.gemini import gemini_model
from prompts.system_prompt import agent_system_prompt_template
from tools.toolbox import Toolbox
from prompts.format_prompt import formats


# Tools used by the Agent
TOOLS = [basic_calculator, weather_forecaster, reddit_scrapper, search_tool, scrape_tool]

# Provider to models map (can be enhanced to fetch dynamically)
PROVIDER_MODELS: Dict[str, List[str]] = {
    "Groq": [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
    ],
    "Gemini": [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ],
    "Mistral": [
        "open-mistral-7b",
        "open-mixtral-8x7b",
        "mistral-large-latest",
        "codestral-latest",
    ],
}


def create_agent(provider: str, model_name: str, api_key: Optional[str]):
    if provider == "Groq":
        model_cls = llama_3_1_70B
    elif provider == "Gemini":
        model_cls = gemini_model
    else:  # Mistral official
        model_cls = mistral_model
    return Agent(tools=TOOLS, model=model_cls, model_name=model_name, model_api_key=api_key)


def build_system_prompt_preview() -> str:
    tb = Toolbox()
    tb.store_tools(TOOLS)
    tools_str = tb.output_tools()
    return agent_system_prompt_template.format(tools=tools_str)


def refresh_models(provider: str, groq_key: str, gemini_key: str, mistral_key: str) -> List[str]:
    try:
        if provider == "Groq":
            from groq import Groq
            key = (groq_key or "").strip()
            if not key:
                return PROVIDER_MODELS["Groq"]
            client = Groq(api_key=key)
            # Groq SDK: client.models.list() -> has data attribute
            resp = client.models.list()
            names = [m.id for m in getattr(resp, "data", []) if hasattr(m, "id")]
            return names or PROVIDER_MODELS["Groq"]
        elif provider == "Gemini":
            import google.generativeai as genai
            key = (gemini_key or "").strip()
            if key:
                genai.configure(api_key=key)
            models = genai.list_models()
            names = []
            for m in models:
                # only include text generation capable models
                caps = getattr(m, "supported_generation_methods", [])
                if "generateContent" in caps or "createContent" in caps:
                    names.append(m.name)
            return names or PROVIDER_MODELS["Gemini"]
        else:
            # Mistral official REST API
            import requests as _rq
            token = (mistral_key or "").strip()
            if not token:
                return PROVIDER_MODELS["Mistral"]
            headers = {"Authorization": f"Bearer {token}"}
            url = "https://api.mistral.ai/v1/models"
            r = _rq.get(url, headers=headers, timeout=15)
            if r.ok:
                data = r.json()
                names = [m.get("id") for m in data.get("data", []) if m.get("id")]
                return names or PROVIDER_MODELS["Mistral"]
            return PROVIDER_MODELS["Mistral"]
    except Exception:
        return PROVIDER_MODELS.get(provider, [])


def parse_reddit_to_df(text: str) -> Optional[pd.DataFrame]:
    if not text:
        return None
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    rows = []
    for b in blocks:
        title = re.search(r"Title:\s*(.*)", b)
        score = re.search(r"Score:\s*(\d+)", b)
        body = re.search(r"Body:\s*(.*)", b, re.DOTALL)
        if title or score or body:
            rows.append({
                "Title": title.group(1).strip() if title else "",
                "Score": int(score.group(1)) if score else None,
                "Body": body.group(1).strip() if body else "",
            })
    if rows:
        return pd.DataFrame(rows)
    return None


def parse_weather_to_dict(text: str) -> Optional[dict]:
    if not text:
        return None
    lines = [l.strip() for l in text.splitlines() if ":" in l]
    data = {}
    for l in lines:
        try:
            key, val = l.split(":", 1)
            data[key.strip()] = val.strip().replace("°C", "").strip()
        except Exception:
            continue
    if data:
        # Convert numeric fields where possible
        for k in ["Temperature", "Feels like", "Min temperature", "Max temperature", "Humidity"]:
            if k in data:
                try:
                    data[k] = float(re.sub(r"[^\d.\-]", "", data[k]))
                except Exception:
                    pass
        return data
    return None


def geocode_city(city: str) -> Optional[Tuple[float, float]]:
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": city, "format": "json", "limit": 1}
        headers = {"User-Agent": "FreeThinker-Gradio-App"}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        js = resp.json()
        if js:
            lat = float(js[0]["lat"])  # type: ignore
            lon = float(js[0]["lon"])  # type: ignore
            return lat, lon
    except Exception:
        return None
    return None


def make_map_html(city: str) -> Optional[str]:
    coords = geocode_city(city)
    if not coords:
        return None
    lat, lon = coords
    fmap: Map = folium.Map(location=[lat, lon], zoom_start=10)
    Marker([lat, lon], tooltip=city).add_to(fmap)
    return fmap._repr_html_()


def run_query(prompt: str, provider: str, model_name: str, custom_model: str,
              groq_key: str, gemini_key: str, hf_key: str,
              serper_key: str, weather_key: str, reddit_client_id: str, reddit_client_secret: str):
    # Choose api key based on provider
    api_key = None
    if provider == "Groq":
        api_key = groq_key.strip() or None
    elif provider == "Gemini":
        api_key = gemini_key.strip() or None
    else:
        api_key = hf_key.strip() or None

    # Use custom model if provided
    model_to_use = custom_model.strip() or model_name

    # Export auxiliary keys to environment for tools
    if serper_key.strip():
        os.environ["SERPER_API_KEY"] = serper_key.strip()
    if weather_key.strip():
        os.environ["WEATHER_API_KEY"] = weather_key.strip()
    if reddit_client_id.strip():
        os.environ["CLIENT_ID"] = reddit_client_id.strip()
    if reddit_client_secret.strip():
        os.environ["CLIENT_SECRET"] = reddit_client_secret.strip()

    agent = create_agent(provider, model_to_use, api_key)
    result = agent.execute(prompt)

    # Base outputs
    raw_output = result.get("output", "")
    table_df = None
    fig = None
    map_html = None

    tool_name = result.get("tool_name")

    if tool_name == "reddit_scrapper":
        table_df = parse_reddit_to_df(raw_output)
        # Optional chart: bar of scores
        if table_df is not None and "Score" in table_df.columns:
            try:
                fig = px.bar(table_df, x="Title", y="Score", title="Reddit Top Posts Scores")
            except Exception:
                fig = None

    elif tool_name == "weather_forecaster":
        weather = parse_weather_to_dict(raw_output)
        if weather:
            # Chart temperatures
            chart_df = pd.DataFrame({
                "Metric": ["Temperature", "Feels like", "Min temperature", "Max temperature"],
                "Value": [weather.get("Temperature"), weather.get("Feels like"), weather.get("Min temperature"), weather.get("Max temperature")],
            })
            try:
                fig = px.bar(chart_df, x="Metric", y="Value", title="Weather Metrics (°C)")
            except Exception:
                fig = None
            # Try to map city from prompt
            map_html = make_map_html(prompt)

    # Convert DataFrame to Gradio Dataframe (pandas is acceptable directly)
    return raw_output, table_df, fig, map_html


with gr.Blocks(title="FreeThinker - Gradio UI") as demo:
    gr.Markdown("""
    # FreeThinker UI
    Ask anything. The agent will choose a tool. Results are presented as:
    - Raw output text
    - Table (if applicable, e.g., Reddit)
    - Chart (if applicable, e.g., Weather or Reddit scores)
    - Map (if applicable, e.g., Weather city)
    """)

    with gr.Row():
        prompt = gr.Textbox(label="Your prompt", placeholder="e.g., Get today's weather in London", scale=2)
        submit = gr.Button("Run", variant="primary")

    with gr.Row():
        provider = gr.Dropdown(label="Provider", choices=["Groq", "Gemini", "Mistral"], value="Groq")
        model_name = gr.Dropdown(label="Model", choices=PROVIDER_MODELS["Groq"], value=PROVIDER_MODELS["Groq"][0])
        custom_model = gr.Textbox(label="Custom model (optional)", placeholder="Override with any valid model id")
        refresh = gr.Button("Refresh Models")

    with gr.Row():
        groq_key = gr.Textbox(label="GROQ_API_KEY", type="password", placeholder="Enter Groq API Key if using Groq")
        gemini_key = gr.Textbox(label="GOOGLE_API_KEY", type="password", placeholder="Enter Google API Key if using Gemini")
        hf_key = gr.Textbox(label="MISTRAL_API_KEY", type="password", placeholder="Enter Mistral API Key if using Mistral provider")

    with gr.Row():
        serper_key = gr.Textbox(label="SERPER_API_KEY", type="password", placeholder="For Search tool (google.serper.dev)")
        weather_key = gr.Textbox(label="WEATHER_API_KEY", type="password", placeholder="For Weather tool (OpenWeather)")
        reddit_client_id = gr.Textbox(label="REDDIT CLIENT_ID", type="password", placeholder="For Reddit tool")
        reddit_client_secret = gr.Textbox(label="REDDIT CLIENT_SECRET", type="password", placeholder="For Reddit tool")

    raw_output = gr.Textbox(label="Raw Output", lines=10)
    table = gr.Dataframe(label="Table", interactive=False)
    chart = gr.Plot(label="Chart")
    map_comp = gr.HTML(label="Map")

    with gr.Accordion("Prompts (System and Format)", open=False):
        sys_prompt_md = gr.Markdown(value=f"""### Active System Prompt\n\n````\n{build_system_prompt_preview()}\n````""")
        fmt_selector = gr.Dropdown(label="Format prompt key", choices=list(formats.keys()), value=list(formats.keys())[0])
        fmt_prompt = gr.Markdown()
        def _show_format(k: str):
            return f"````\n{formats[k]}\n````"
        fmt_selector.change(fn=_show_format, inputs=fmt_selector, outputs=fmt_prompt)

    def update_models(provider_choice: str):
        return gr.update(choices=PROVIDER_MODELS.get(provider_choice, []),
                         value=(PROVIDER_MODELS.get(provider_choice, [""])[0] if PROVIDER_MODELS.get(provider_choice) else ""))

    provider.change(fn=update_models, inputs=provider, outputs=model_name)
    def do_refresh(pv: str, gk: str, gmk: str, mk: str):
        names = refresh_models(pv, gk, gmk, mk)
        default = names[0] if names else ""
        return gr.update(choices=names, value=default)
    refresh.click(fn=do_refresh, inputs=[provider, groq_key, gemini_key, hf_key], outputs=model_name)

    submit.click(
        run_query,
        inputs=[prompt, provider, model_name, custom_model, groq_key, gemini_key, hf_key, serper_key, weather_key, reddit_client_id, reddit_client_secret],
        outputs=[raw_output, table, chart, map_comp]
    )

if __name__ == "__main__":
    demo.launch()
