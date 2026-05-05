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
    [data-testid="stMetric"] {
        background-color: #1a1c24;
        border: 2px solid #333;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #FFD700 !important;
        font-size: 22px !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 34px !important;
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
            
            # --- DEFINE GROUPS ---
            row_top = [c for c in all_cols if c.upper() in ["TK", "K"]]
            row_mid = [c for c in all_cols if any(x in c.upper() for x in ["1ST", "2ND", "3RD"])]
            row_bot = [c for c in all_cols if any(x in c.upper() for x in ["4TH", "5TH"])]
            other_teams = [c for c in all_cols if c not in row_top and c not in row_mid and c not in row_bot]

            # --- RENDER ROW 1: TK & K ---
            if row_top:
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                cols1 = st.columns(len(row_top))
                for i, team in enumerate(row_top):
                    with cols1[i]:
                        val = str(match[team].values).strip("[]'\"")
                        if val.lower() in ['nan', 'none', '']: val = "---"
                        st.metric(label=team, value=val)

            # --- RENDER ROW 2: 1st, 2nd, 3rd ---
            if row_mid:
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                cols2 = st.columns(3)
                for i, team in enumerate(row_mid):
                    with cols2[i]:
                        val = str(match[team].values).strip("[]'\"")
                        if val.lower() in ['nan', 'none', '']: val = "---"
                        st.metric(label=team, value=val)

            # --- RENDER ROW 3: 4th & 5th ---
            if row_bot:
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                cols3 = st.columns(2)
                for i, team in enumerate(row_bot):
                    with cols3[i]:
                        val = str(match[team].values).strip("[]'\"")
                        if val.lower() in ['nan', 'none', '']: val = "---"
                        st.metric(label=team, value=val)

            # --- RENDER ANY OTHERS ---
            if other_teams:
                st.divider()
                cols_other = st.columns(len(other_teams))
                for i, team in enumerate(other_teams):
                    with cols_other[i]:
                        val = str(match[team].values).strip("[]'\"")
                        if val.lower() in ['nan', 'none', '']: val = "---"
                        st.metric(label=team, value=val)
        else:
            st.info(f"No specific activities scheduled for {current_slot}.")
    else:
        st.error("Missing 'Time' column.")

update_dashboard()
