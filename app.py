import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Phelan Falcons Live Schedule", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SETTINGS ---
# Your specific Google Sheet ID
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
        margin-bottom: 2px;
    }
    /* Vertical Stack Styling - Compact & Scaled */
    [data-testid="stMetric"] {
        background-color: #1a1c24;
        border: 2px solid #333;
        padding: 8px 15px; 
        border-radius: 10px;
        margin-bottom: 5px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        color: #FFD700 !important;
        font-size: 20px !important;
        font-weight: bold !important;
        width: 100%;
        text-align: center;
        line-height: 1.2;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 32px !important;
        width: 100%;
        text-align: center;
        line-height: 1.2;
    }
    /* Keep the vertical gap tight */
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
    
    # Weekend Handling: Defaults to Monday for testing on weekends
    if current_day in ["Saturday", "Sunday"]:
        current_day = "Monday"

    # Rounds down to the nearest 5-minute mark for the Excel search
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
        st.error("Error connecting to Google Sheets. Ensure your Sheet ID is correct and shared as 'Anyone with the link can view'.")
        return

    time_col = next((col for col in df.columns if col.lower() == 'time'), None)

    if time_col:
        df[time_col] = df[time_col].astype(str)
        # Match current 5-minute block
        match = df[df[time_col].str.contains(current_slot, na=False)]

        if not match.empty:
            all_cols = [c for c in df.columns if c != time_col and "Unnamed" not in c]
            
            # --- DYNAMIC TIER LOGIC ---
            top_tier = [c for c in all_cols if c.upper() in ["TK", "K"]]
            mid_tier = [c for c in all_cols if any(x in c.upper() for x in ["1ST", "2ND", "3RD"])]
            bot_tier = [c for c in all_cols if any(x in c.upper() for x in ["4TH", "5TH"])]
            
            # Automatically catch any new columns added later
            used_cols = top_tier + mid_tier + bot_tier
            other_tier = [c for c in all_cols if c not in used_cols]

            def render_row(teams_list):
                if teams_list:
                    cols = st.columns(len(teams_list))
                    for i, team in enumerate(teams_list):
                        with cols[i]:
                            val = str(match[team].values).strip("[]'\"")
                            if val.lower() in ['nan', 'none', '']: val = "---"
                            st.metric(label=team, value=val)

            # RENDER THE DASHBOARD LAYOUT
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            render_row(top_tier)    # TK, K
            render_row(mid_tier)    # 1st, 2nd, 3rd
            render_row(bot_tier)    # 4th, 5th
            render_row(other_tier)  # Any new columns added to Google Sheets
            
        else:
            st.info(f"No specific activities scheduled for the {current_slot} interval.")
    else:
        st.error("Could not find a 'Time' column in your Google Sheet.")

# --- 4. RUN THE APP ---
update_dashboard()
