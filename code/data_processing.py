import os
import glob
import pandas as pd
from pathlib import Path

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleanup:
      - Drop fully empty rows/columns
      - Normalize column names (lowercase, underscores, strip non-alphanumerics)
      - Strip whitespace from strings
      - Coerce numeric columns where possible
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
    One CSV per sheet, named <excel_stem>_<sheet_name>.csv
    """
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    excel_files = glob.glob(os.path.join(input_folder, "*.xlsx"))
    if not excel_files:
        print(f"No .xlsx files found in {input_folder}")
        return

    for xfile in excel_files:
        stem = Path(xfile).stem
        # Read all sheets
        sheets = pd.read_excel(xfile, sheet_name=None)
        for sheet_name, df in sheets.items():
            cleaned = clean_df(df)
            # sanitize sheet name for filename
            safe_sheet = sheet_name.strip().replace(" ", "_")
            out_path = os.path.join(
                output_folder,
                f"{stem}_{safe_sheet}.csv"
            )
            cleaned.to_csv(out_path, index=False)
            print(f"Written: {out_path}")

if __name__ == "__main__":
    convert_and_clean()

