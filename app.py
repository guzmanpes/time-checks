import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Team Status Command Center", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CUSTOM THEMING (CSS) ---
st.markdown("""
    <style>
    /* Background and Main Title */
    .main {
        background-color: #0e1117;
    }
    h1 {
        color: #00d4ff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-align: center;
        padding-bottom: 0px;
    }
    .stSubheader {
        text-align: center;
        color: #888;
    }
    
    /* Style each Metric Card */
    [data-testid="stMetric"] {
        background-color: #1a1c24;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #00d4ff;
    }
    
    /* Label and Value styling */
    [data-testid="stMetricLabel"] {
        color: #00d4ff !important;
        font-size: 20px !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 34px !important;
    }
    
    /* Hide Streamlit branding */
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

    # --- HEADER SECTION ---
    st.markdown(f"<h1>TEAM STATUS COMMAND CENTER</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #888; font-size: 20px;'>{current_day} | {now.strftime('%I:%M:%S %p')} | Interval: {current_slot}</p>", unsafe_allow_html=True)
    st.divider()

    # --- LOAD DATA ---
    try:
        df = pd.read_excel("schedule.xlsx", sheet_name=current_day, engine='openpyxl').astype(object)
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Error: Could not find sheet '{current_day}'")
        return

    time_column = next((col for col in df.columns if col.lower() == 'time'), None)

    if time_column:
        df[time_column] = df[time_column].astype(str)
        match = df[df[time_column].str.contains(current_slot, na=False)]

        if not match.empty:
            teams = [c for c in df.columns if c != time_column]
            
            # Use columns to create a "Grid"
            # Adjust the number 3 or 4 based on how many cards you want per row
            rows = [teams[i:i + 3] for i in range(0, len(teams), 3)]
            
            for row in rows:
                cols = st.columns(3)
                for i, team in enumerate(row):
                    with cols[i]:
                        raw_val = match[team].values
                        clean_text = str(raw_val).strip("[]'\"")
                        if clean_text.lower() in ['nan', 'none', '']:
                            clean_text = "OFF DUTY"
                        
                        st.metric(label=team, value=clean_text)
        else:
            st.info(f"System Standby: No specific activities scheduled for {current_slot}.")
    else:
        st.error("Time column missing.")

update_dashboard()
