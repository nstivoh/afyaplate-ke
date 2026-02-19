# filepath: core/pdf_extractor.py
import streamlit as st
import pandas as pd
import camelot
import tabula
import pdfplumber
import numpy as np
import re
from pathlib import Path

# --- CONFIGURATION ---
PDF_PATH = Path(__file__).parent.parent / "data" / "KFCT_2018.pdf"
OUTPUT_CSV_PATH = Path(__file__).parent.parent / "data" / "kfct_clean.csv"
START_PAGE = 29
END_PAGE = 202

# Pages with "Lattice" tables (Cereals and their products)
LATTICE_PAGES = "30-37"

# --- Main Function ---
def extract_and_clean_pdf(pdf_path=PDF_PATH):
    """
    Orchestrates the entire PDF extraction and cleaning process.
    Uses a hybrid approach: Camelot for lattice tables, Tabula for stream tables.
    """
    if not pdf_path.exists():
        st.error(f"PDF file not found at: {pdf_path}")
        return pd.DataFrame()

    progress_bar = st.progress(0, text="Starting PDF extraction...")

    # Step 1: Extract tables using Camelot for specific lattice-like pages
    try:
        progress_bar.progress(5, text="Extracting tables from Cereal pages (30-37) with Camelot...")
        lattice_tables = camelot.read_pdf(
            str(pdf_path),
            pages=LATTICE_PAGES,
            flavor='lattice',
            line_scale=40
        )
        lattice_dfs = [table.df for table in lattice_tables]
        st.write(f"Camelot found {len(lattice_dfs)} tables on pages {LATTICE_PAGES}.")
    except Exception as e:
        st.warning(f"Camelot (Lattice) extraction failed: {e}. Falling back to Tabula for all pages.")
        lattice_dfs = []


    # Step 2: Extract tables from all relevant pages using Tabula for stream-like data
    progress_bar.progress(20, text="Extracting tables from all pages (29-202) with Tabula...")
    try:
        stream_tables = tabula.read_pdf(
            str(pdf_path),
            pages=f"{START_PAGE}-{END_PAGE}",
            multiple_tables=True,
            stream=True,
            guess=False,
            pandas_options={'header': None}
        )
        st.write(f"Tabula found {len(stream_tables)} tables between pages {START_PAGE}-{END_PAGE}.")
    except Exception as e:
        st.error(f"Tabula (Stream) extraction failed: {e}")
        stream_tables = []

    progress_bar.progress(50, text="Processing and cleaning extracted tables...")

    # Combine dataframes
    all_dfs = lattice_dfs + stream_tables

    if not all_dfs:
        st.error("No tables could be extracted from the PDF.")
        return pd.DataFrame()

    # Step 3: Clean and standardize the dataframes
    cleaned_dfs = [clean_table(df) for df in all_dfs]

    # Step 4: Concatenate all cleaned dataframes
    full_df = pd.concat(cleaned_dfs, ignore_index=True)

    # Step 5: Post-processing on the concatenated dataframe
    final_df = post_process_data(full_df)

    progress_bar.progress(90, text=f"Saving cleaned data to {OUTPUT_CSV_PATH}...")

    # Step 6: Save to CSV
    final_df.to_csv(OUTPUT_CSV_PATH, index=False)

    progress_bar.progress(100, text="Extraction complete!")
    st.success(f"Successfully extracted and saved {len(final_df)} food items.")

    return final_df


def clean_table(df):
    """
    Performs initial cleaning on a single dataframe extracted from the PDF.
    """
    # Drop empty rows and columns
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    df = df.reset_index(drop=True)

    # Clean cell values: replace newlines and weird characters
    df = df.applymap(lambda x: str(x).replace('
', ' ').replace('', ' ').strip() if isinstance(x, str) else x)

    return df

def standardize_columns(df):
    """
    Identifies and renames columns to a standard format based on common nutrient names.
    This is a heuristic-based approach and might need refinement.
    """
    # Define a mapping of potential column fragments to standard names
    column_map = {
        'code': 'food_code',
        'food': 'food_name_english',
        'water': 'water_g',
        'energy': 'energy_kcal',
        'protein': 'protein_g',
        'fat': 'fat_g',
        'carbohydrate': 'carbs_g',
        'fibre': 'fibre_g',
        'ca': 'calcium_mg', 'calcium': 'calcium_mg',
        'fe': 'iron_mg', 'iron':셔츠': 'iron_mg',
        'zn': 'zinc_mg', 'zinc': 'zinc_mg',
        'vit a': 'vit_a_rae_mcg', 'retinol': 'vit_a_rae_mcg',
        'thiamin': 'thiamin_mg',
        'riboflavin': 'riboflavin_mg',
        'niacin': 'niacin_mg',
        'vit c': 'vit_c_mg'
    }

    new_columns = []
    header_row = find_header_row(df)
    
    if header_row is None:
        return df # Can't process if no header is found

    for col in df.columns:
        col_name = str(df.iloc[header_row][col]).lower()
        found = False
        for key, value in column_map.items():
            if key in col_name:
                new_columns.append(value)
                found = True
                break
        if not found:
            new_columns.append(f"unknown_{col}")
            
    df.columns = new_columns
    # Drop the header row and rows above it
    df = df.iloc[header_row + 1:].reset_index(drop=True)
    return df

def find_header_row(df):
    """Find the most likely header row by looking for keywords."""
    for i, row in df.iterrows():
        row_str = ' '.join(str(v).lower() for v in row.values)
        if 'food' in row_str and 'protein' in row_str and 'energy' in row_str:
            return i
    return 0 # Default to first row if no better header is found

def post_process_data(df):
    """
    Final cleaning, type conversion, and categorization on the combined dataframe.
    """
    # A very basic attempt to get a single food name and code column
    # This part is extremely tricky due to varied formats.
    # We assume the first two columns are often code and name.
    if len(df.columns) > 1:
        df.rename(columns={df.columns[0]: 'col1', df.columns[1]: 'col2'}, inplace=True)

        # Heuristic: food code is often numeric or alphanumeric like 'A001'
        df['food_code'] = df['col1'].apply(lambda x: x if re.match(r'^[A-Z]?[0-9]{1,4}$', str(x).strip()) else None)
        df['food_name_english'] = df.apply(lambda row: row['col2'] if row['food_code'] is not None else row['col1'], axis=1)

        # Fill forward food codes for multiline food names
        df['food_code'] = df['food_code'].ffill()

        # Try to identify the header row again and rename columns properly
        df = standardize_columns(df)
        
    # Remove rows that are just headers repeated
    df = df[~df['protein_g'].str.contains('protein', case=False, na=False)]

    # Clean numeric columns
    nutrient_cols = [
        'energy_kcal', 'protein_g', 'fat_g', 'carbs_g', 'fibre_g',
        'calcium_mg', 'iron_mg', 'zinc_mg', 'vit_a_rae_mcg', 'thiamin_mg',
        'riboflavin_mg', 'niacin_mg', 'vit_c_mg'
    ]

    for col in nutrient_cols:
        if col in df.columns:
            # Extract numbers, handling footnotes like "tr" (trace) or "*"
            df[col] = df[col].astype(str).str.extract(r'(\d+\.?\d*)', expand=False)
            # Convert to numeric, coercing errors to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Add category column (simple heuristic based on food code)
    df['category'] = df['food_code'].str[0].map({
        'A': 'Cereals and their products',
        'B': 'Starchy roots, tubers, and their products',
        'C': 'Legumes, and their products',
        'D': 'Nuts, seeds and their products',
        'E': 'Vegetables and their products',
        'F': 'Fruits and their products',
        'G': 'Meat, poultry and their products',
        'H': 'Fish, other aquatic animals and their products',
        'J': 'Milk, milk products and eggs',
        'K': 'Oils and fats',
        'L': 'Beverages',
        'M': 'Spices and condiments',
        'N': 'Miscellaneous',
        'P': 'Infant foods',
        'S': 'Foods for special dietary use',
    }).fillna('Uncategorized')

    # Final cleanup
    df = df.dropna(subset=['food_name_english'])
    df = df[df['food_name_english'].str.len() > 2] # Remove very short/invalid names
    df = df.drop_duplicates(subset=['food_code', 'food_name_english'])
    
    # Select and order final columns
    final_cols = ['food_code', 'food_name_english', 'category'] + nutrient_cols
    df = df[[col for col in final_cols if col in df.columns]]

    return df.reset_index(drop=True)

# Example of how to run this from the Streamlit app
if __name__ == '__main__':
    st.title("PDF Extractor Test")
    if st.button("Run Extraction"):
        with st.spinner("Extracting KFCT 2018 PDF... This may take a minute or two."):
            result_df = extract_and_clean_pdf()
            if not result_df.empty:
                st.dataframe(result_df)
                st.info(f"Data saved to {OUTPUT_CSV_PATH}")

```