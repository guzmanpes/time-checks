import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Team Live Status", layout="wide")

# Custom CSS for styling the dashboard
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
    # --- LOAD DATA ---
    try:
        # Load and immediately force into 'object' mode to prevent <ArrowString> errors
        df = pd.read_excel("schedule.xlsx", engine='openpyxl').astype(object)
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Error: Could not find 'schedule.xlsx'. Ensure it is uploaded to GitHub.")
        return

    # --- CLOCK LOGIC (FIXED TO US/PACIFIC) ---
    local_tz = pytz.timezone('US/Pacific') 
    now = datetime.now(local_tz)
    
    # Rounds down to the nearest 5-minute mark for the Excel search
    rounded_minute = (now.minute // 5) * 5
    current_slot = now.replace(minute=rounded_minute, second=0, microsecond=0).strftime("%H:%M")

    # --- UI HEADER ---
    st.title("🕒 Team Live Status Dashboard")
    st.write(f"**Pacific Time:** {now.strftime('%I:%M:%S %p')} | **Interval:** {current_slot}")
    st.divider()

    # --- FIND DATA ---
    time_column = next((col for col in df.columns if col.lower() == 'time'), None)

    if time_column:
        df[time_column] = df[time_column].astype(str)
        
        # Search for the row matching the current 5-minute slot
        match = df[df[time_column].str.contains(current_slot, na=False)]

        if not match.empty:
            # Get list of all teams (all columns except Time)
            teams = [c for c in df.columns if c != time_column]
            
            # Create columns dynamically
            cols = st.columns(len(teams))

            for i, team in enumerate(teams):
                with cols[i]:
                    # Grab the value and clean up brackets/quotes
                    raw_val = match[team].values
                    clean_text = str(raw_val).strip("[]'\"")
                    
                    # Handle empty cells or errors
                    if clean_text.lower() in ['nan', 'none', '']:
                        clean_text = "---"
                    
                    st.metric(label=team, value=clean_text)
        else:
            st.warning(f"No entry found in Excel for interval: {current_slot}")
            st.info("Ensure your Excel 'Time' column has leading zeros if necessary (e.g., 08:05).")
    else:
        st.error("Could not find a 'Time' column in your Excel file.")

# --- 3. RUN THE APP ---
update_dashboard()
