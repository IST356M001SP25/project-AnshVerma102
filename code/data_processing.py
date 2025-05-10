# app.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Ensure cache folder exists
CACHE_DIR = "./cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# 2. Paths
SUMMARY_CSV = os.path.join(CACHE_DIR, "label_share_summary.csv")
DETAIL_CSV  = os.path.join(CACHE_DIR, "label_share_detail.csv")

# 3. Sidebar controls
st.sidebar.header("⚙️ Controls")
refresh      = st.sidebar.button("🔄 Refresh data from Spotify")
label_filter = st.sidebar.radio(
    "🎚️ Label type",
    ("All", "Majors", "Indies"),
    index=0,
)

# 4. Title
st.title("🎛️ Spotify Label Share Monitor")

@st.cache_data(show_spinner=True)
def load_data(do_refresh: bool):
    # if cached CSVs exist & no refresh, just load them
    if not do_refresh and os.path.exists(SUMMARY_CSV):
        df_sum    = pd.read_csv(SUMMARY_CSV)
        df_detail = pd.read_csv(DETAIL_CSV)
        return df_sum, df_detail

    # otherwise re-fetch from Spotify
    from data import fetch_and_transform
    df_sum, df_detail = fetch_and_transform(summary_csv_path=SUMMARY_CSV)
    return df_sum, df_detail

# 5. Load
df_summary, df_detail = load_data(refresh)

# 6. Define major labels set
MAJOR_LABELS = {
    "Universal Music Group",
    "Sony Music Entertainment",
    "Warner Music Group",
}
# 7. Filter
if label_filter == "Majors":
    df_plot = df_summary[df_summary["label"].isin(MAJOR_LABELS)]
elif label_filter == "Indies":
    df_plot = df_summary[~df_summary["label"].isin(MAJOR_LABELS)]
else:
    df_plot = df_summary.copy()

# 8. Treemap
st.markdown("### 📊 Label Share Treemap")
fig = px.treemap(
    df_plot,
    path=["label"],
    values="album_count",
    title="Number of New Releases by Label",
)
st.plotly_chart(fig, use_container_width=True)

# 9. Bar chart of average popularity
st.markdown("### 🎵 Average Popularity by Label")
fig2 = px.bar(
    df_plot.sort_values("avg_popularity", ascending=False),
    x="avg_popularity",
    y="label",
    orientation="h",
    title="Avg. Popularity of New Releases",
)
st.plotly_chart(fig2, use_container_width=True)

# 10. Download buttons
st.markdown("---")
st.download_button(
    label="📥 Download summary CSV",
    data=open(SUMMARY_CSV, "rb"),
    file_name="label_share_summary.csv",
    mime="text/csv",
)
st.download_button(
    label="📥 Download detail CSV",
    data=open(DETAIL_CSV, "rb"),
    file_name="label_share_detail.csv",
    mime="text/csv",
)
