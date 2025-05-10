# data.py
from dotenv import load_dotenv
import os
import pandas as pd
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# ─── Authentication Setup ────────────────────────────────────────────────
# Load variables from .env into os.environ
load_dotenv()  

CLIENT_ID     = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError(
        "Spotify credentials missing: set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in your .env"
    )

auth_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# ─── Data Fetch & Transform ─────────────────────────────────────────────
def fetch_and_transform(summary_csv_path: str):
    sp = Spotify(client_credentials_manager=auth_manager)

    # 1. Fetch 50 newest releases (US)
    new_releases = sp.new_releases(limit=50, country="US")["albums"]["items"]
    album_ids = [alb["id"] for alb in new_releases]

    # 2. Batch-fetch album details (label, popularity, release_date)
    details = []
    for i in range(0, len(album_ids), 20):
        batch = album_ids[i : i + 20]
        albums = sp.albums(batch)["albums"]
        for alb in albums:
            details.append({
                "album_id":     alb["id"],
                "album_name":   alb["name"],
                "label":        alb.get("label", "Unknown"),
                "popularity":   alb.get("popularity", 0),
                "release_date": alb.get("release_date"),
            })

    df_detail = pd.DataFrame(details)

    # 3. Summarize by label
    df_summary = (
        df_detail
        .groupby("label", as_index=False)
        .agg(
            album_count    = ("album_id",   "count"),
            avg_popularity = ("popularity", "mean")
        )
        .sort_values("album_count", ascending=False)
    )

    # 4. Write CSVs to cache
    df_summary.to_csv(summary_csv_path, index=False)
    detail_csv = summary_csv_path.replace("summary", "detail")
    df_detail.to_csv(detail_csv, index=False)

    return df_summary, df_detail
