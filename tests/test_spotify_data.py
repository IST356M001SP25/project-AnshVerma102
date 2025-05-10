import os
import pandas as pd
import pytest

# import the function under test
from code.spotify_data import fetch_and_transform

# A dummy Spotify client to avoid real API calls
class DummySpotify:
    def new_releases(self, limit, country):
        # pretend we got two album IDs
        return {"albums": {"items": [{"id": "a1"}, {"id": "a2"}]}}

    def albums(self, ids):
        # return a mini “albums” payload for each requested ID
        albums = []
        for album_id in ids:
            # alternate labels / popularity for test coverage
            if album_id == "a1":
                label = "Test Label"
                pop   = 50
            else:
                label = "Universal Music USA"
                pop   = 80
            albums.append({
                "id":           album_id,
                "name":         f"Album {album_id}",
                "label":        label,
                "popularity":   pop,
                "release_date": "2025-01-01"
            })
        return {"albums": albums}

# Fixture to monkeypatch Spotify and env vars
@pytest.fixture(autouse=True)
def patch_spotify(monkeypatch, tmp_path, monkeypatch):
    import spotify_data
    # always return our DummySpotify
    monkeypatch.setattr(spotify_data, "Spotify", lambda client_credentials_manager: DummySpotify())
    # ensure creds present
    monkeypatch.setenv("SPOTIPY_CLIENT_ID", "dummy_id")
    monkeypatch.setenv("SPOTIPY_CLIENT_SECRET", "dummy_secret")
    yield

def test_fetch_and_transform_creates_csv(tmp_path):
    # arrange: a fresh path in tmp_path
    summary_csv = tmp_path / "label_share_summary.csv"

    # act
    df_sum, df_detail = fetch_and_transform(str(summary_csv))

    # assert: CSV files exist
    assert summary_csv.exists()
    detail_csv = summary_csv.parent / "label_share_detail.csv"
    assert detail_csv.exists()

    # assert: summary DataFrame has expected columns
    assert set(df_sum.columns) == {"label", "album_count", "avg_popularity"}

    # assert: contents match our DummySpotify logic
    row_test_label = df_sum[df_sum["label"] == "Test Label"]
    assert row_test_label["album_count"].iloc[0] == 1
    assert row_test_label["avg_popularity"].iloc[0] == 50

    row_major = df_sum[df_sum["label"] == "Universal Music USA"]
    assert row_major["album_count"].iloc[0] == 1
    assert row_major["avg_popularity"].iloc[0] == 80
