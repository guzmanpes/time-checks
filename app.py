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
        margin-bottom: 5px;
    }
    /* Vertical Stack Styling */
    [data-testid="stMetric"] {
        background-color: #1a1c24;
        border: 2px solid #333;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px; /* Space between vertical rows */
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        color: #FFD700 !important;
        font-size: 24px !important;
        font-weight: bold !important;
        width: 100%;
        text-align: center;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 40px !important;
        width: 100%;
        text-align: center;
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
    st.markdown(f"<p style='text-align: center; color: #BBB; font-size: 20px;'>{current_day} | {now.strftime('%I:%M:%S %p')} | Slot: {current_slot}</p>", unsafe_allow_html=True)

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
            # Get all teams in the order they appear in Excel (or manual list)
            teams = [c for c in df.columns if c != time_col]
            
            # --- VERTICAL RENDER ---
            # Instead of columns, we just loop through and display them one by one
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            
            for team in teams:
                val = str(match[team].values).strip("[]'\"")
                if val.lower() in ['nan', 'none', '']: 
                    val = "---"
                
                # Each st.metric naturally takes up the full width when not in a column
                st.metric(label=team, value=val)
                
        else:
            st.info(f"No specific activities scheduled for {current_slot}.")
    else:
        st.error("Missing 'Time' column.")

update_dashboard()
