# data.py
import pandas as pd
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_CREDS = SpotifyClientCredentials()

def fetch_and_transform(summary_csv_path: str):
    sp = Spotify(client_credentials_manager=CLIENT_CREDS)

    # fetch 50 new releases
    new = sp.new_releases(limit=50, country="US")["albums"]["items"]
    ids = [a["id"] for a in new]

    details = []
    for i in range(0, len(ids), 20):
        batch = ids[i : i + 20]
        for alb in sp.albums(batch)["albums"]:
            details.append({
                "album_id":     alb["id"],
                "album_name":   alb["name"],
                "label":        alb.get("label", "Unknown"),
                "popularity":   alb.get("popularity", 0),
                "release_date": alb.get("release_date"),
            })

    df_detail = pd.DataFrame(details)
    df_summary = (
        df_detail
        .groupby("label", as_index=False)
        .agg(
            album_count    = ("album_id", "count"),
            avg_popularity = ("popularity", "mean")
        )
        .sort_values("album_count", ascending=False)
    )

    # save both
    df_summary.to_csv(summary_csv_path, index=False)
    df_detail.to_csv(summary_csv_path.replace("summary", "detail"), index=False)

    return df_summary, df_detail

