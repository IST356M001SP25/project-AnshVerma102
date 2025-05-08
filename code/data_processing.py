#!/usr/bin/env python3
import os
import glob
import pandas as pd
from pathlib import Path

def detect_header_row(raw: pd.DataFrame, max_rows: int = 20, lookahead: int = 50) -> int:
    """
    Among the first `max_rows`, choose the row that:
      - Isn’t overly numeric itself (so we avoid picking a year-row or pure data row)
      - Yields the most numeric cells in the next `lookahead` rows (i.e. real data)
    """
    best_idx = 0
    best_score = -1

    for idx in range(min(max_rows, len(raw) - 1)):
        header = raw.iloc[idx]
        non_empty = header.notna().sum()
        if non_empty == 0:
            continue

        # how many header cells parse as numeric?
        numeric_in_header = pd.to_numeric(header, errors='coerce').notna().sum()
        frac_numeric = numeric_in_header / non_empty

        # skip if header is more than half numeric
        if frac_numeric > 0.5:
            continue

        # look at the block of rows below as “data”—count numeric cells
        block = raw.iloc[idx+1 : idx+1+lookahead]
        numeric_data_cells = (
            pd.to_numeric(block.stack(), errors='coerce')
              .notna()
              .sum()
        )

        # pick the header_row that maximizes numeric_data_cells
        if numeric_data_cells > best_score:
            best_score = numeric_data_cells
            best_idx = idx

    return best_idx

def load_with_dynamic_header(path: str, sheet_name: str) -> pd.DataFrame:
    """
    Read without header, detect & promote the real header row, drop above it.
    """
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)
    hdr = detect_header_row(raw, max_rows=20, lookahead=100)
    df = raw.iloc[hdr+1 : ].copy().reset_index(drop=True)
    df.columns = raw.iloc[hdr].astype(str)
    return df

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Drop empty rows/cols
    - Clean column names to snake_case
    - Drop one-char columns
    - Strip string whitespace & coerce numerics
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

    df = df.loc[:, df.columns.str.len() > 1]

    for c in df.select_dtypes(include='object'):
        df[c] = df[c].astype(str).str.strip().replace({'nan': pd.NA})

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

    for fx in files:
        stem = Path(fx).stem
        sheets = pd.ExcelFile(fx).sheet_names
        for sh in sheets:
            raw = load_with_dynamic_header(fx, sh)
            cleaned = clean_df(raw)

            safe_sh = str(sh).strip().replace(" ", "_")
            out = os.path.join(output_folder, f"{stem}_{safe_sh}.csv")
            cleaned.to_csv(out, index=False)
            print(f"Wrote → {out}")

if __name__ == "__main__":
    convert_and_clean()

