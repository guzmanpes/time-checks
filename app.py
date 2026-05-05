import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Team Live Status", layout="wide")

# Custom CSS
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

# --- 2. THE DASHBOARD FUNCTION ---
@st.fragment(run_every=5)
def update_dashboard():
    # --- CLOCK & DAY LOGIC ---
    local_tz = pytz.timezone('US/Pacific') 
    now = datetime.now(local_tz)
    
    # Get the current day name (e.g., "Monday")
    current_day = now.strftime("%A")
    
    # Weekend Handling: If it's Saturday/Sunday, default to Monday
    if current_day in ["Saturday", "Sunday"]:
        current_day = "Monday"

    # Rounds down to the nearest 5-minute mark for the Excel search
    rounded_minute = (now.minute // 5) * 5
    current_slot = now.replace(minute=rounded_minute, second=0, microsecond=0).strftime("%H:%M")

    # --- LOAD DATA FOR SPECIFIC DAY ---
    try:
        # Added 'sheet_name=current_day' to target the correct tab
        df = pd.read_excel("schedule.xlsx", sheet_name=current_day, engine='openpyxl').astype(object)
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Error: Could not find a sheet named '{current_day}' in your Excel file.")
        st.info("Ensure your Excel tabs are named: Monday, Tuesday, Wednesday, Thursday, Friday")
        return

    # --- UI HEADER ---
    st.title("🕒 Team Live Status Dashboard")
    st.write(f"**Day:** {current_day} | **Pacific Time:** {now.strftime('%I:%M:%S %p')} | **Interval:** {current_slot}")
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
                    raw_val = match[team].values[0]
                    clean_text = str(raw_val).strip("[]'\"")
                    
                    if clean_text.lower() in ['nan', 'none', '']:
                        clean_text = "---"
                    
                    st.metric(label=team, value=clean_text)
        else:
            st.warning(f"No entry found in the **{current_day}** sheet for interval: {current_slot}")
    else:
        st.error(f"Could not find a 'Time' column in the {current_day} sheet.")

# --- 3. RUN THE APP ---
update_dashboard()