#!/usr/bin/env python3
import os
import glob
import pandas as pd
from pathlib import Path

def detect_header_row(raw: pd.DataFrame, max_rows: int = 20) -> int:
    """
    Among the first `max_rows`, pick the row with the most non-empty, non-numeric cells.
    That tends to be the actual header in mixed tables.
    """
    best_idx = 0
    best_score = -1
    for idx in range(min(max_rows, len(raw))):
        row = raw.iloc[idx]
        # which cells are non-null?
        non_empty = row.notna()
        # which cells parse as numeric?
        numeric = pd.to_numeric(row, errors='coerce').notna()
        # non-numeric & non-empty
        non_numeric = non_empty & ~numeric
        score = non_numeric.sum()
        if score > best_score:
            best_score = score
            best_idx = idx
    return best_idx

def load_with_dynamic_header(path: str, sheet_name: str) -> pd.DataFrame:
    """
    Read the sheet with no header, detect which row is the real header,
    then drop everything above it and assign column names.
    """
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)
    header_row = detect_header_row(raw, max_rows=20)
    # everything below header_row
    df = raw.iloc[header_row + 1 :].copy().reset_index(drop=True)
    # assign the actual header names
    df.columns = raw.iloc[header_row].astype(str)
    return df

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Drop empty rows/cols
    - Normalize col-names to snake_case
    - Strip whitespace in strings
    - Coerce numerics
    - Drop any column whose name ends up a single character
    """
    df = df.dropna(axis=0, how='all').dropna(axis=1, how='all')

    cols = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r'\s+', '_', regex=True)
          .str.replace(r'[^\w_]', '', regex=True)
    )
    df.columns = cols

    # drop one-letter columns
    df = df.loc[:, df.columns.str.len() > 1]

    # trim strings
    for c in df.select_dtypes(include='object'):
        df[c] = df[c].astype(str).str.strip().replace({'nan': pd.NA})

    # coerce numerics
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='ignore')

    return df

def convert_and_clean(
    input_folder: str = "cache",
    output_folder: str = "cache/cleaned_csvs"
):
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    files = glob.glob(os.path.join(input_folder, "*.xlsx"))
    if not files:
        print(f"No .xlsx files in {input_folder}")
        return

    for f in files:
        stem = Path(f).stem
        sheets = pd.ExcelFile(f).sheet_names
        for sh in sheets:
            raw = load_with_dynamic_header(f, sh)
            cleaned = clean_df(raw)

            safe_sh = sh.strip().replace(" ", "_")
            out = os.path.join(output_folder, f"{stem}_{safe_sh}.csv")
            cleaned.to_csv(out, index=False)
            print(f"Wrote {out}")

if __name__ == "__main__":
    convert_and_clean()
