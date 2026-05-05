import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Phelan Falcons Live Schedule", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SETTINGS ---
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
        margin-bottom: 2px; /* Reduced header margin */
    }
    /* Vertical Stack Styling - Compact Version */
    [data-testid="stMetric"] {
        background-color: #1a1c24;
        border: 2px solid #333;
        padding: 8px 15px; /* Reduced vertical padding from 15px to 8px */
        border-radius: 10px;
        margin-bottom: 5px; /* Reduced space between rows from 10px to 5px */
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        color: #FFD700 !important;
        font-size: 20px !important; /* Slightly smaller label */
        font-weight: bold !important;
        width: 100%;
        text-align: center;
        line-height: 1.2;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 32px !important; /* Slightly smaller value text */
        width: 100%;
        text-align: center;
        line-height: 1.2;
    }
    /* Shrink the gap between the Tier rows */
    .stVerticalBlock {
        gap: 0.5rem !important;
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
    st.markdown(f"<p style='text-align: center; color: #BBB; font-size: 18px; margin-top: -10px;'>{current_day} | {now.strftime('%I:%M:%S %p')} | Slot: {current_slot}</p>", unsafe_allow_html=True)

    # --- LOAD DATA FROM GOOGLE SHEETS ---
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={current_day}"
        df = pd.read_csv(url).astype(object)
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error("Error connecting to Google Sheets. Check ID and Share settings.")
        return

    time_col = next((col for col in df.columns if col.lower() == 'time'), None)

    if time_col:
        df[time_col] = df[time_col].astype(str)
        match = df[df[time_col].str.contains(current_slot, na=False)]

        if not match.empty:
            all_cols = [c for c in df.columns if c != time_col and "Unnamed" not in c]
            
            # --- TIER LOGIC ---
            top_tier = [c for c in all_cols if c.upper() in ["TK", "K"]]
            mid_tier = [c for c in all_cols if any(x in c.upper() for x in ["1ST", "2ND", "3RD"])]
            bot_tier = [c for c in all_cols if any(x in c.upper() for x in ["4TH", "5TH"])]

            def render_row(teams_list):
                if teams_list:
                    cols = st.columns(len(teams_list))
                    for i, team in enumerate(teams_list):
                        with cols[i]:
                            val = str(match[team].values).strip("[]'\"")
                            if val.lower() in ['nan', 'none', '']: val = "---"
                            st.metric(label=team, value=val)

            # RENDER TIERS (Using tight spacing)
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            render_row(top_tier)
            render_row(mid_tier)
            render_row(bot_tier)
            
        else:
            st.info(f"No specific activities scheduled for the {current_slot} interval.")
    else:
        st.error("Could not find a 'Time' column in your Google Sheet.")

# --- 4. RUN THE APP ---
update_dashboard()
