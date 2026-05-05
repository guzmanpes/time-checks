import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Phelan Falcons Live Schedule", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CUSTOM THEMING (CSS) ---
st.markdown("""
    <style>
    /* Background and Main Title */
    .main {
        background-color: #0e1117;
    }
    h1 {
        color: #FFD700; /* Gold color for Falcons theme */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-align: center;
        padding-bottom: 0px;
        text-shadow: 2px 2px 4px #000000;
    }
    
    /* Style each Metric Card */
    [data-testid="stMetric"] {
        background-color: #1a1c24;
        border: 2px solid #333;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #FFD700; /* Glow gold on hover */
    }
    
    /* Label and Value styling */
    [data-testid="stMetricLabel"] {
        color: #FFD700 !important;
        font-size: 22px !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 36px !important;
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
    
    # Weekend Handling
    if current_day in ["Saturday", "Sunday"]:
        current_day = "Monday"

    rounded_minute = (now.minute // 5) * 5
    current_slot = now.replace(minute=rounded_minute, second=0, microsecond=0).strftime("%H:%M")

    # --- HEADER SECTION ---
    st.markdown(f"<h1>PHELAN FALCONS DAILY LIVE SCHEDULE</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #BBB; font-size: 20px;'>{current_day} | {now.strftime('%I:%M:%S %p')} | Current Slot: {current_slot}</p>", unsafe_allow_html=True)
    st.divider()

    # --- LOAD DATA ---
    try:
        df = pd.read_excel("schedule.xlsx", sheet_name=current_day, engine='openpyxl').astype(object)
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Error: Could not find sheet '{current_day}' in schedule.xlsx")
        return

    time_column = next((col for col in df.columns if col.lower() == 'time'), None)

    if time_column:
        df[time_column] = df[time_column].astype(str)
        match = df[df[time_column].str.contains(current_slot, na=False)]

        if not match.empty:
            teams = [c for c in df.columns if c != time_column]
            
            # Grid Logic: 3 cards per row
            rows = [teams[i:i + 3] for i in range(0, len(teams), 3)]
            
            for row in rows:
                cols = st.columns(3)
                for i, team in enumerate(row):
                    with cols[i]:
                        raw_val = match[team].values
                        clean_text = str(raw_val).strip("[]'\"")
                        if clean_text.lower() in ['nan', 'none', '']:
                            clean_text = "---"
                        
                        st.metric(label=team, value=clean_text)
        else:
            st.info(f"No specific activities scheduled for the {current_slot} interval.")
    else:
        st.error("Missing 'Time' column in the Excel sheet.")

update_dashboard()
