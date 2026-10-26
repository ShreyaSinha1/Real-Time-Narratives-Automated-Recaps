import streamlit as st
import pandas as pd
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize Streamlit Page Config
st.set_page_config(page_title="Football Innovation Studio", layout="wide")
st.title("⚽ Real-Time Football Narratives & Automated Recaps")

# Initialize LLM (Ensure OPENAI_API_KEY environment variable is set)
try:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
except Exception:
    st.error("Please set your OPENAI_API_KEY environment variable.")
    st.stop()

# 1. Mock Database of Live Events (Simulating real-time API feeds)
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

# 2. Prompts for Narrative & Recap Generation
narrative_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an elite, dramatic football live-text commentator. Turn the provided event into an engaging, single-paragraph narrative update. Keep it punchy, matching the game tempo."),
    ("user", "Minute: {minute} | Team: {team} | Player: {player} | Event: {event} | Context: {detail}")
])

recap_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a chief sports journalist writing the final match report. Based on the complete chronological match event log, write a 3-paragraph compelling match recap. Include a catchy headline, highlight tactical turning points, and name a man of the match."),
    ("user", "Full Match Log:\n{full_log}")
])

narrative_chain = narrative_prompt | llm | StrOutputParser()
recap_chain = recap_prompt | llm | StrOutputParser()

# UI Layout Components
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📡 Live Match Event Stream")
    sim_button = st.button("Simulate Next Live Match Event ➡️")
    
    if sim_button and st.session_state.current_step < len(mock_events):
        event = mock_events[st.session_state.current_step]
        st.session_state.current_step += 1
        
        # Run Live Narrative Generation
        with st.spinner("Generating live narrative..."):
            narrative = narrative_chain.invoke({
                "minute": event["minute"],
                "team": event["team"],
                "player": event["player"],
                "event": event["event"],
                "detail": event["detail"]
            })
            st.session_state.narrative_log.insert(0, {"minute": event["minute"], "text": narrative})
            
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
            final_recap = recap_chain.invoke({"full_log": full_log_str})
            st.markdown(final_recap)
    else:
        st.info(f"Progressing through match events ({st.session_state.current_step}/{len(mock_events)}). Complete the match to generate the full automated summary.")
