import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Phelan Falcons Live Schedule", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SETTINGS ---
# Your Google Sheet ID must be inside quotation marks
SHEET_ID = "1N3QLjiX4o8IwsDtGiJno-uQQ4ySijRXdy7Z7ec2kAdw"

# --- 3. CUSTOM THEMING (CSS) ---
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
    [data-testid="stMetric"] {
        background-color: #1a1c24;
        border: 2px solid #333;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        color: #FFD700 !important;
        font-size: 26px !important;
        font-weight: bold !important;
        width: 100%;
        text-align: center;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 44px !important;
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
    
    # Weekend Handling
    if current_day in ["Saturday", "Sunday"]:
        current_day = "Monday"

    # Rounds down to the nearest 5-minute mark
    rounded_minute = (now.minute // 5) * 5
    current_slot = now.replace(minute=rounded_minute, second=0, microsecond=0).strftime("%H:%M")

    # --- HEADER ---
    st.markdown(f"<h1>PHELAN FALCONS DAILY LIVE SCHEDULE</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #BBB; font-size: 20px;'>{current_day} | {now.strftime('%I:%M:%S %p')} | Slot: {current_slot}</p>", unsafe_allow_html=True)

    # --- LOAD DATA FROM GOOGLE SHEETS ---
    try:
        # We use the SHEET_ID variable defined at the top
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={current_day}"
        df = pd.read_csv(url).astype(object)
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error("Error connecting to Google Sheets. Check your Sheet ID and ensure 'Anyone with the link' can view.")
        return

    time_col = next((col for col in df.columns if col.lower() == 'time'), None)

    if time_col:
        df[time_col] = df[time_col].astype(str)
        match = df[df[time_col].str.contains(current_slot, na=False)]

        if not match.empty:
            teams = [c for c in df.columns if c != time_col and "Unnamed" not in c]
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            for team in teams:
                val = str(match[team].values).strip("[]'\"")
                if val.lower() in ['nan', 'none', '']: 
                    val = "---"
                st.metric(label=team, value=val)
        else:
            st.info(f"No specific activities scheduled for the {current_slot} interval.")
    else:
        st.error("Could not find a 'Time' column in your Google Sheet.")

# --- 4. RUN THE APP ---
update_dashboard()
