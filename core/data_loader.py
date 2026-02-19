# filepath: core/data_loader.py
import streamlit as st
import pandas as pd
import json
from pathlib import Path

# Define paths relative to this file
DATA_DIR = Path(__file__).parent.parent / "data"
CLEAN_KFCT_CSV_PATH = DATA_DIR / "kfct_clean.csv"
PRICES_JSON_PATH = DATA_DIR / "prices_nairobi_2026.json"
CLIENT_DIR = DATA_DIR / "clients"

@st.cache_data
def load_food_data():
    """
    Loads the cleaned Kenya Food Composition Tables (KFCT) data from the CSV file.
    Uses Streamlit's data caching to avoid reloading on every interaction.
    Returns an empty DataFrame if the file doesn't exist.
    """
    if not CLEAN_KFCT_CSV_PATH.exists():
        st.error(f"Cleaned data file not found: {CLEAN_KFCT_CSV_PATH}. Please run the PDF extraction first from the 'Settings' tab.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(CLEAN_KFCT_CSV_PATH)
        # Add a Swahili name column for future use (can be populated later)
        if 'food_name_swahili' not in df.columns:
            df['food_name_swahili'] = ""
        # Add a 'display_name' for search
        df['display_name'] = df['food_name_english']
        return df
    except Exception as e:
        st.error(f"Error loading food data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_prices_data():
    """
    Loads the Nairobi 2026 prices from the JSON file.
    Uses caching and returns a dictionary.
    """
    if not PRICES_JSON_PATH.exists():
        st.warning(f"Price file not found: {PRICES_JSON_PATH}. Using empty price list.")
        return {}
    try:
        with open(PRICES_JSON_PATH, 'r') as f:
            prices = json.load(f)
        return prices
    except json.JSONDecodeError as e:
        st.error(f"Error reading prices file (invalid JSON): {e}")
        return {}
    except Exception as e:
        st.error(f"Error loading prices data: {e}")
        return {}

def save_prices_data(prices_dict):
    """
    Saves the updated prices dictionary to the JSON file.
    """
    try:
        with open(PRICES_JSON_PATH, 'w') as f:
            json.dump(prices_dict, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Failed to save prices: {e}")
        return False

def get_client_files():
    """Returns a list of saved client JSON files."""
    CLIENT_DIR.mkdir(exist_ok=True)
    return list(CLIENT_DIR.glob("*.json"))

def save_client_data(client_name, data):
    """Saves a client's data to a JSON file."""
    CLIENT_DIR.mkdir(exist_ok=True)
    file_name = f"{client_name.replace(' ', '_').lower()}.json"
    file_path = CLIENT_DIR / file_name
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return file_path
    except Exception as e:
        st.error(f"Error saving client data: {e}")
        return None

def load_client_data(file_path):
    """Loads a client's data from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading client data from {file_path}: {e}")
        return None

# To run this file for testing:
if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.title("Data Loader Test")

    st.subheader("Food Data (`kfct_clean.csv`)")
    food_df = load_food_data()
    if not food_df.empty:
        st.dataframe(food_df)
        st.success(f"Successfully loaded {len(food_df)} food items.")
    else:
        st.warning("Food data is empty. The CSV might be missing or unreadable.")

    st.divider()

    st.subheader("Price Data (`prices_nairobi_2026.json`)")
    prices = load_prices_data()
    if prices:
        st.json(prices)
        st.success(f"Successfully loaded {len(prices)} price entries.")
    else:
        st.warning("Price data is empty.")

```