# filepath: app.py
import streamlit as st
from pathlib import Path

# --- Page Configuration ---
st.set_page_config(
    page_title="🇰🇪 AfyaPlate KE",
    page_icon="🇰🇪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Import Core and Component Modules ---
from core.data_loader import (
    load_food_data,
    load_prices_data,
    save_prices_data,
    get_client_files,
    CLIENT_DIR,
)
from core.pdf_extractor import extract_and_clean_pdf, PDF_PATH, OUTPUT_CSV_PATH
from components.food_search import show_food_search
from components.meal_planner_ui import show_meal_planner_ui
from components.report_generator import show_report_generator
import json
from components.home_page import show_home_page

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Main App ---

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="title"><span class="title-flag">🇰🇪</span>AfyaPlate KE</div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Built by Stephen – Kenyan Registered Dietitian Nutritionist</p>', unsafe_allow_html=True)
    st.divider()

    st.markdown("## Theme")
    theme = st.selectbox("Select Theme", ["Light", "Dark"])
    if theme == "Light":
        load_css("assets/light.css")
    else:
        load_css("assets/dark.css")
    
    st.divider()
    st.info("Get the Pro version for extra recipes and custom meal models!", icon="🌟")
    
    st.markdown("---")
    st.markdown("[⭐ Star on GitHub](https://github.com/nstivoh/afyaplate-ke)", unsafe_allow_html=True)
    st.markdown("[❤️ Sponsor this Project](https://github.com/sponsors/nstivoh)", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<small>100% local • Privacy first</small>", unsafe_allow_html=True)


# --- Data Loading ---
# Load data once and cache it
food_data = load_food_data()


# --- Tab/Page Routing ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "🔍 Food Search", "🍽️ Automated Meal Planner", "📄 Client Reports", "⚙️ Settings"])

with tab1:
    show_home_page()

with tab2:
    show_food_search(food_data)

with tab3:
    show_meal_planner_ui(food_data)

with tab4:
    show_report_generator()

with tab5:
    st.title("⚙️ Settings & Data Management")
    st.write("Manage the application's data and settings.")

    # --- PDF Extraction Section ---
    with st.expander("Extract Food Data from PDF", expanded=not OUTPUT_CSV_PATH.exists()):
        st.markdown(f"""
        This tool extracts and cleans the food composition data from the `KFCT_2018.pdf` file.
        
        - **Source:** `{PDF_PATH}`
        - **Output:** `{OUTPUT_CSV_PATH}`
        
        **This is a one-time process that can take 1-3 minutes.**
        """)
        if st.button("Start PDF Extraction", disabled=not PDF_PATH.exists()):
            with st.spinner("Extracting... This will take a while. Please wait."):
                extract_and_clean_pdf()
            st.success("Extraction complete! The app will now use the new data.")
            st.info("You may need to restart the app or refresh the page to see changes.")
            st.rerun()
        if not PDF_PATH.exists():
            st.error(f"PDF source file not found at {PDF_PATH}. Please make sure it's in the data directory.")

    # --- Price Editor Section ---
    with st.expander("Edit Food Prices"):
        st.markdown("Edit the prices for common foods used in cost calculations. Prices are in KSh per unit.")
        
        prices_data = load_prices_data()
        if prices_data:
            edited_prices = st.data_editor(
                prices_data,
                width='stretch'
            )
            if st.button("Save Price Changes"):
                if save_prices_data(edited_prices):
                    st.success("Prices updated successfully!")
                    st.cache_data.clear() # Clear cache to reload new prices
                    st.rerun()
                else:
                    st.error("Failed to save prices.")
        else:
            st.warning("Price data file could not be loaded.")

    # --- Client Data Management ---
    with st.expander("Manage Client Data"):
        st.markdown("View and manage locally saved client data files.")
        CLIENT_DIR.mkdir(exist_ok=True)
        client_files = list(CLIENT_DIR.glob("*.json"))
        
        if not client_files:
            st.info("No client files found.")
        else:
            st.write("Found the following client files:")
            for f in client_files:
                st.text(f.name)
            
            if st.button("⚠️ Clear All Client Data", type="primary"):
                for f in client_files:
                    f.unlink()
                st.success("All client data has been deleted.")
                st.rerun()
    
    # --- Planner Backend Settings ---
    with st.expander("Planner Backend Settings", expanded=True):
        st.markdown("""
        Choose the backend for generating meal plans.
        - **Gemini:** Uses Google's API. Requires an internet connection and an API key.
        """)

        # Initialize session state for settings if they don't exist
        if 'planner_backend' not in st.session_state:
            st.session_state.planner_backend = "Gemini" # Default to API-first
        if 'gemini_api_key' not in st.session_state:
            st.session_state.gemini_api_key = ""
        if 'ollama_model' not in st.session_state:
            st.session_state.ollama_model = "deepseekcoderafya"

        # UI for backend selection
        st.session_state.planner_backend = st.selectbox(
            "Select Planner Backend",
            ("Gemini",), # "Ollama" is hidden but code remains
            index=0
        )

        # UI for specific backend settings
        if st.session_state.planner_backend == "Ollama":
            st.session_state.ollama_model = st.text_input(
                "Ollama Model Name",
                value=st.session_state.ollama_model
            )
            st.caption("Ensure this model is available in your local Ollama instance (`ollama pull <model_name>`).")
        
        elif st.session_state.planner_backend == "Gemini":
            st.session_state.gemini_api_key = st.text_input(
                "Gemini API Key",
                value=st.session_state.gemini_api_key,
                type="password",
                help="Get your key from Google AI Studio."
            )
            st.warning("""
            **Security Warning:** For simplicity, this UI saves your key in the session. 
            For production use, it is strongly recommended to use Streamlit Secrets.
            Add your key to a `.streamlit/secrets.toml` file like this:
            `GEMINI_API_KEY = "YOUR_KEY_HERE"`
            """, icon="🔒")

        st.success(f"Backend set to **{st.session_state.planner_backend}**.")