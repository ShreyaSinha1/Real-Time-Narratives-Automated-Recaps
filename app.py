import streamlit as st
import pandas as pd
import time
import os
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 🛠️ Load environment variables from the local .env file
load_dotenv()

# Initialize Streamlit Page Config
st.set_page_config(page_title="Premier League Studio - Match Insights Engine", layout="wide")
st.title("⚽ Synthetic Match Insights Engine | Real-Time Narratives & Automated Recaps")

# 🔑 Fetch API Credentials from .env
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("❌ Missing Credentials: Could not find 'GROQ_API_KEY' inside your .env file.")
    st.stop()

# 📡 Dynamically fetch current active models from Groq using the .env token
@st.cache_data(show_spinner=False)
def fetch_active_groq_models(api_key):
    try:
        url = "https://groq.com"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            models_data = response.json().get("data", [])
            # Filter out audio/whisper models to show text models only
            model_ids = [m["id"] for m in models_data if "whisper" not in m["id"].lower()]
            if model_ids:
                return sorted(model_ids)
    except Exception:
        pass
    # Updated active fallbacks reflecting recent Groq model deprecations
    return ["qwen/qwen3.8-27b", "openai/gpt-oss-20b"]

# Sidebar layout configuration for Model Selection
st.sidebar.header("🤖 Engine Configuration")
available_models = fetch_active_groq_models(groq_api_key)
selected_model = st.sidebar.selectbox("Select Active Free Model:", available_models)
st.sidebar.success(f"Running engine on: `{selected_model}`")

# Initialize Free LLM Engine using the selected model and credentials
try:
    llm = ChatGroq(model=selected_model, temperature=0.7, groq_api_key=groq_api_key)
except Exception as e:
    st.error(f"Failed to initialize Free LLM Engine. Error details: {e}")
    st.stop()

# Mock Database of Live Events (Simulating real-time Premier League API feeds)
mock_events = [
    {"minute": "01'", "team": "Arsenal", "player": "Bukayo Saka", "event": "Kickoff", "detail": "Match begins at the Emirates."},
    {"minute": "14'", "team": "Chelsea", "player": "Cole Palmer", "event": "Yellow Card", "detail": "Tactical foul stopping a counter-attack."},
    {"minute": "32'", "team": "Arsenal", "player": "Kai Havertz", "event": "GOAL", "detail": "Header from a Martin Odegaard corner kick. 1-0."},
    {"minute": "45+2'", "team": "System", "player": "Referee", "event": "Half Time", "detail": "Teams head into tunnels. Arsenal dominates possession."},
    {"minute": "61'", "team": "Chelsea", "player": "Nicolas Jackson", "event": "GOAL", "detail": "Clinical finish after an error by Saliba. 1-1."},
    {"minute": "78'", "team": "Arsenal", "player": "Declan Rice", "event": "Red Card", "detail": "Second yellow card given for delaying the restart."},
    {"minute": "89'", "team": "Chelsea", "player": "Cole Palmer", "event": "GOAL", "detail": "Stunning long-range strike into the top corner! 1-2."},
    {"minute": "90+4'", "team": "System", "player": "Referee", "event": "Full Time", "detail": "Chelsea pulls off a dramatic comeback win away from home."}
]

# Session State to hold simulated live timeline progress
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "narrative_log" not in st.session_state:
    st.session_state.narrative_log = []

# Prompts for Narrative & Recap Generation
narrative_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an elite, dramatic football live-text commentator. Turn the provided event into an engaging, single-paragraph narrative update. Keep it punchy, matching the game tempo."),
    ("user", "Minute: {minute} | Team: {team} | Player: {player} | Event: {event} | Context: {detail}")
])

recap_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a chief sports journalist writing the final match report. Based on the complete chronological match event log, write a 3-paragraph compelling match recap. Include a catchy headline, highlight tactical turning points, and name a man of the match."),
    ("user", "Full Match Log:\n{full_log}")
])

# Build pipeline chains
narrative_chain = narrative_prompt | llm | StrOutputParser()
recap_chain = recap_prompt | llm | StrOutputParser()

# UI Layout Components
col1, col2 = st.columns(2)

with col1:
    st.subheader("📡 Live Match Event Stream")
    sim_button = st.button("Simulate Next Live Match Event ➡️")
    
    if sim_button and st.session_state.current_step < len(mock_events):
        event = mock_events[st.session_state.current_step]
        st.session_state.current_step += 1
        
        # Run Live Narrative Generation
        with st.spinner("Generating live narrative..."):
            try:
                narrative = narrative_chain.invoke({
                    "minute": event["minute"],
                    "team": event["team"],
                    "player": event["player"],
                    "event": event["event"],
                    "detail": event["detail"]
                })
                st.session_state.narrative_log.insert(0, {"minute": event["minute"], "text": narrative})
            except Exception as api_err:
                st.error(f"Engine Error: {api_err}")
            
    # Display the live commentary feed
    for comment in st.session_state.narrative_log:
        st.markdown(f"**[{comment['minute']}]** {comment['text']}")

with col2:
    st.subheader("📰 Automated Post-Match Recap")
    if st.session_state.current_step >= len(mock_events):
        st.success("🏁 Match Finished! Generating final automated recap report...")
        
        # Build raw string text from all mock logs for summary input
        full_log_str = "\n".join([f"{e['minute']} - {e['team']} - {e['player']} - {e['event']}: {e['detail']}" for e in mock_events])
        
        with st.spinner("Compiling tactical match review..."):
            try:
                final_recap = recap_chain.invoke({"full_log": full_log_str})
                st.markdown(final_recap)
            except Exception as api_err:
                st.error(f"Failed to generate recap: {api_err}")
    else:
        st.info(f"Progressing through match events ({st.session_state.current_step}/{len(mock_events)}). Complete the match to generate the full automated summary.")
