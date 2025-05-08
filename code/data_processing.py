
import os
import glob
import pandas as pd
from pathlib import Path

def detect_header_row(df_raw: pd.DataFrame, max_rows: int = 10) -> int:
    """
    Find the row within the first `max_rows` that has the most non-null entries.
    Return its index; we'll treat that as the header.
    """
    counts = df_raw.iloc[:max_rows].notna().sum(axis=1)
    # pick the earliest row with the maximum count
    return int(counts.idxmax())

def load_with_dynamic_header(path: str, sheet_name: str) -> pd.DataFrame:
    """
    Read sheet entirely with no header, detect and promote the 'true' header row,
    then return the DataFrame below it.
    """
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)
    header_row = detect_header_row(raw)
    # slice off everything above and including header_row
    df = raw.iloc[header_row + 1 :].copy()
    # assign column names
    df.columns = raw.iloc[header_row].astype(str)
    # reset index
    df.reset_index(drop=True, inplace=True)
    return df

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleanup:
      - Drop fully empty rows/columns
      - Normalize column names (lowercase, underscores, alphanumerics only)
      - Strip whitespace from strings
      - Coerce numeric columns where possible
      - Drop columns whose cleaned name is a single character
    """
    # Drop rows/cols that are entirely NA
    df = df.dropna(axis=0, how='all').dropna(axis=1, how='all')
    
    # Clean column names
    clean_cols = (
        df.columns
          .astype(str)
          .str.strip()
          .str.lower()
          .str.replace(r'\s+', '_', regex=True)
          .str.replace(r'[^\w_]', '', regex=True)
    )
    df.columns = clean_cols

    # Drop one-letter columns
    df = df.loc[:, df.columns.str.len() > 1]

    # Strip whitespace in object (string) columns
    obj_cols = df.select_dtypes(include='object').columns
    for col in obj_cols:
        df[col] = df[col].astype(str).str.strip().replace({'nan': pd.NA})

    # Attempt to convert any column to numeric (where sensible)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    
    return df

def convert_and_clean(
    input_folder: str = "cache",
    output_folder: str = "cache/cleaned_csvs"
):
    """
    Read all .xlsx files in input_folder, clean them, and export CSVs to output_folder.
    Header rows are auto-detected. Single-character columns are dropped.
    """
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    excel_files = glob.glob(os.path.join(input_folder, "*.xlsx"))
    if not excel_files:
        print(f"No .xlsx files found in {input_folder}")
        return

    for xfile in excel_files:
        stem = Path(xfile).stem
        # read all sheet names
        sheet_names = pd.ExcelFile(xfile).sheet_names
        for sheet_name in sheet_names:
            # load with dynamic header
            df_raw = load_with_dynamic_header(xfile, sheet_name)
            cleaned = clean_df(df_raw)
            
            # sanitize sheet name for filename
            safe_sheet = str(sheet_name).strip().replace(" ", "_")
            out_path = os.path.join(
                output_folder,
                f"{stem}_{safe_sheet}.csv"
            )
            cleaned.to_csv(out_path, index=False)
            print(f"→ Written: {out_path}")

if __name__ == "__main__":
    convert_and_clean()
