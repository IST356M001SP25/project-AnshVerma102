import pandas as pd
import pytest

# pull in your keyword list
from app.py import MAJOR_KEYWORDS

def test_label_keyword_filtering():
    # make a small summary-like DataFrame
    df = pd.DataFrame({
        "label": [
            "Universal Music Group",
            "Sony Music Entertainment US",
            "Warner Music Sweden",
            "Indie X Records"
        ],
        "album_count":    [5, 3, 2, 7],
        "avg_popularity": [70, 60, 80, 30]
    })

    # build the mask exactly as in your app
    pattern = "|".join(MAJOR_KEYWORDS)
    mask = df["label"].str.contains(pattern, case=False, na=False)

    majors = df[mask]
    indies = df[~mask]

    # should catch 3 majors
    assert len(majors) == 3
    assert "Indie X Records" not in majors["label"].values

    # indies should be just the one
    assert len(indies) == 1
    assert indies["label"].iloc[0] == "Indie X Records"
