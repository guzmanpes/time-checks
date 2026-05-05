import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Team Live Status", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
        color: #1E88E5;
    }
    [data-testid="stMetricLabel"] {
        font-size: 16px;
        color: #555555;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE AUTO-REFRESH FUNCTION ---
# This "fragment" allows the app to refresh itself every 5 seconds
@st.fragment(run_every=5)
def update_dashboard():
    # --- LOAD DATA ---
    try:
        df = pd.read_excel("schedule.xlsx", engine='openpyxl').astype(object)
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Error: Could not find 'schedule.xlsx'.")
        return

    # --- CLOCK LOGIC ---
    now = datetime.now()
    rounded_minute = (now.minute // 5) * 5
    current_slot = now.replace(minute=rounded_minute, second=0, microsecond=0).strftime("%H:%M")

    # --- UI HEADER ---
    st.title("🕒 Team Live Status Dashboard")
    st.write(f"Current Time: **{now.strftime('%H:%M:%S')}** | Current Interval: **{current_slot}**")
    st.divider()

    # --- FIND DATA ---
    time_column = next((col for col in df.columns if col.lower() == 'time'), None)

    if time_column:
        df[time_column] = df[time_column].astype(str)
        match = df[df[time_column].str.contains(current_slot, na=False)]

        if not match.empty:
            teams = [c for c in df.columns if c != time_column]
            cols = st.columns(len(teams))

            for i, team in enumerate(teams):
                with cols[i]:
                    raw_val = match[team].values
                    clean_text = str(raw_val).strip("[]'\"")
                    
                    if clean_text.lower() in ['nan', 'none', '']:
                        clean_text = "---"
                    
                    st.metric(label=team, value=clean_text)
        else:
            st.warning(f"No entry found for interval: {current_slot}")
    else:
        st.error("Could not find a 'Time' column in your Excel file.")

# --- 3. RUN THE DASHBOARD ---
update_dashboard()