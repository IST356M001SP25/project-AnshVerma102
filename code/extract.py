import streamlit as st
import spotipy as sp
import pandas as pd
@st.cache_data(ttl=3600)
def fetch_and_cache_new_releases():
    # Fetch the first page of new releases (0–49)
    new_rel = sp.new_releases(limit=50)["albums"]["items"]
    album_ids = [alb["id"] for alb in new_rel]

    # Batch‐fetch full album details (to get the `label` & `popularity`)
    details = sp.albums(album_ids)["albums"]

    # Build a flat record per album
    records = []
    for alb in details:
        records.append({
            "album_id":      alb["id"],
            "album_name":    alb["name"],
            "label":         alb.get("label", "Unknown"),
            "release_date":  alb["release_date"],
            "popularity":    alb["popularity"],
            "total_tracks":  alb["total_tracks"],
        })

    df = pd.DataFrame(records)
    # Save to CSV for reproducibility & offline mode
    df.to_csv(CACHE_FILE, index=False)
    return df

# On app startup:
df_albums = fetch_and_cache_new_releases()
st.write("Fetched and cached:", len(df_albums), "albums")
sp = spotipy.Spotify(auth_manager=auth_manager)

