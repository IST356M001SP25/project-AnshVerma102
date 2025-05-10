# app.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# ─── Setup cache folder & file paths ─────────────────────────────────────
CACHE_DIR   = "./cache"
os.makedirs(CACHE_DIR, exist_ok=True)

SUMMARY_CSV = os.path.join(CACHE_DIR, "label_share_summary.csv")
DETAIL_CSV  = os.path.join(CACHE_DIR, "label_share_detail.csv")

# ─── Sidebar controls ────────────────────────────────────────────────────
st.sidebar.header("⚙️ Controls")
refresh      = st.sidebar.button("🔄 Refresh data from Spotify")
label_filter = st.sidebar.radio(
    "🎚️ Label type",
    ["All", "Majors", "Indies"]
)

# ─── Page title ──────────────────────────────────────────────────────────
st.title("🎛️ Spotify Label Share Monitor")

# ─── Load or fetch data ──────────────────────────────────────────────────
@st.cache_data(show_spinner=True)
def load_data(do_refresh: bool):
    if not do_refresh and os.path.exists(SUMMARY_CSV):
        df_sum    = pd.read_csv(SUMMARY_CSV)
        df_detail = pd.read_csv(DETAIL_CSV)
    else:
        from data import fetch_and_transform
        df_sum, df_detail = fetch_and_transform(SUMMARY_CSV)
    return df_sum, df_detail

df_summary, df_detail = load_data(refresh)

# ─── Define major labels & apply filter ─────────────────────────────────
MAJOR_LABELS = {
    "Universal Music Group",
    "Sony Music Entertainment",
    "Warner Music Group",
}

if label_filter == "Majors":
    df_plot = df_summary[df_summary["label"].isin(MAJOR_LABELS)]
elif label_filter == "Indies":
    df_plot = df_summary[~df_summary["label"].isin(MAJOR_LABELS)]
else:
    df_plot = df_summary.copy()

# ─── Treemap of album count by label ────────────────────────────────────
st.markdown("### 📊 Label Share Treemap")
fig = px.treemap(
    df_plot,
    path=["label"],
    values="album_count",
    title="Number of New Releases by Label"
)
st.plotly_chart(fig, use_container_width=True)

# ─── Bar chart of average popularity ─────────────────────────────────────
st.markdown("### 🎵 Average Popularity by Label")
fig2 = px.bar(
    df_plot.sort_values("avg_popularity", ascending=False),
    x="avg_popularity",
    y="label",
    orientation="h",
    title="Avg. Popularity of New Releases"
)
st.plotly_chart(fig2, use_container_width=True)

# ─── Download buttons ────────────────────────────────────────────────────
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
