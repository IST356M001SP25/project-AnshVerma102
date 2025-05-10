# app.py
import os
import streamlit as st
import pandas as pd
from data.data import fetch_and_transform

# 1. Ensure cache folder exists
CACHE_DIR = "./cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# 2. Path to our summary CSV
SUMMARY_CSV = os.path.join(CACHE_DIR, "label_share_summary.csv")

# 3. Sidebar controls
st.sidebar.header("Label Share Monitor")
refresh = st.sidebar.button("🔄 Refresh data from Spotify")

# 4. Main title
st.title("🎛️ Spotify Label Share Monitor")

# 5. Load (or refresh) data
@st.cache_data(show_spinner=True)
def load_summary(csv_path: str, do_refresh: bool) -> pd.DataFrame:
    if not do_refresh and os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    # otherwise, rebuild
    from data import fetch_and_transform  # see next section
    df_summary = fetch_and_transform(csv_path)
    return df_summary

df = load_summary(SUMMARY_CSV, refresh)

# 6. Display
st.markdown("### Label Breakdown")
st.dataframe(df)

st.markdown("**Tip:** Click on the header of any column to sort by album count or avg. popularity.")
