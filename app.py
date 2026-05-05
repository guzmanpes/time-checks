import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Phelan Falcons Live Schedule", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CUSTOM THEMING (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    h1 {
        color: #FFD700; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-align: center;
        text-shadow: 2px 2px 4px #000000;
        margin-bottom: 0px;
    }
    .top-bar {
        background-color: #1a1c24;
        border: 2px solid #FFD700;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 20px;
    }
    [data-testid="stMetric"] {
        background-color: #1a1c24;
        border: 2px solid #333;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #FFD700 !important;
        font-size: 20px !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 32px !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

@st.fragment(run_every=5)
def update_dashboard():
    # --- TIME LOGIC ---
    local_tz = pytz.timezone('US/Pacific') 
    now = datetime.now(local_tz)
    current_day = now.strftime("%A")
    if current_day in ["Saturday", "Sunday"]:
        current_day = "Monday"

    rounded_minute = (now.minute // 5) * 5
    current_slot = now.replace(minute=rounded_minute, second=0, microsecond=0).strftime("%H:%M")

    # --- HEADER ---
    st.markdown(f"<h1>PHELAN FALCONS DAILY LIVE SCHEDULE</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #BBB; font-size: 18px;'>{current_day} | {now.strftime('%I:%M:%S %p')} | Slot: {current_slot}</p>", unsafe_allow_html=True)

    # --- LOAD DATA ---
    try:
        df = pd.read_excel("schedule.xlsx", sheet_name=current_day, engine='openpyxl').astype(object)
        df.columns = df.columns.str.strip()
    except Exception:
        st.error(f"Error: Could not find sheet '{current_day}'")
        return

    time_col = next((col for col in df.columns if col.lower() == 'time'), None)

    if time_col:
        df[time_col] = df[time_col].astype(str)
        match = df[df[time_col].str.contains(current_slot, na=False)]

        if not match.empty:
            all_cols = [c for c in df.columns if c != time_col]
            
            # --- TOP BAR (TK and K) ---
            # We identify columns that start with TK or K
            top_teams = [c for c in all_cols if c.upper() in ["TK", "K"]]
            other_teams = [c for c in all_cols if c.upper() not in ["TK", "K"]]

            if top_teams:
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                # Create centered columns for the top bar
                top_cols = st.columns(len(top_teams))
                for i, team in enumerate(top_teams):
                    with top_cols[i]:
                        val = str(match[team].values).strip("[]'\"")
                        if val.lower() in ['nan', 'none', '']: val = "---"
                        st.metric(label=f"⭐ {team}", value=val)
                st.divider()

            # --- GRID (REST OF THE TEAMS) ---
            rows = [other_teams[i:i + 3] for i in range(0, len(other_teams), 3)]
            for row in rows:
                cols = st.columns(3)
                for i, team in enumerate(row):
                    with cols[i]:
                        val = str(match[team].values).strip("[]'\"")
                        if val.lower() in ['nan', 'none', '']: val = "---"
                        st.metric(label=team, value=val)
        else:
            st.info(f"No specific activities scheduled for {current_slot}.")
    else:
        st.error("Missing 'Time' column.")

update_dashboard()
