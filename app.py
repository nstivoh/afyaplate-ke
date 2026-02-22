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

# --- Asset and Branding ---
def load_css():
    st.markdown("""
    <style>
    /* Main colors from config.toml */
    .stApp {
        background_color: #F8F9FA;
    }
    /* Custom title */
    .title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #008000; /* Green */
        display: flex;
        align-items: center;
    }
    .title-flag {
        font-size: 2.5rem;
        margin-right: 10px;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #333;
        font-style: italic;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #F0F2F6;
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #008000; /* Green */
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# --- Main App ---

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="title"><span class="title-flag">🇰🇪</span>AfyaPlate KE</div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Built by Stephen – Kenyan Registered Dietitian Nutritionist</p>', unsafe_allow_html=True)
    st.divider()

    st.markdown("## Navigation")
    # Using radio buttons for tab-like navigation in the sidebar
    app_mode = st.radio(
        "Go to",
        ["🏠 Home", "🔍 Food Search", "🍽️ Automated Meal Planner", "📄 Client Reports", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
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
if app_mode == "🏠 Home":
    st.title("Welcome to AfyaPlate KE")
    st.markdown("Your all-in-one, offline-first nutrition tool designed for Kenyan healthcare professionals.")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Features")
        st.markdown("""
        - **🔍 Food Search:** Instantly search the comprehensive Kenya Food Composition Tables (2018).
        - **🍽️ Automated Meal Planner:** Generate personalized, culturally-aware meal plans.
        - **📄 Client Reports:** Create professional, print-ready PDF reports for your clients.
        - **⚙️ Fully Customizable:** Edit food prices, manage client data, and more.
        - **🔒 Privacy-First:** All your data stays on your computer. No cloud, no internet required after setup.
        """)
    with col2:
        st.image("https://i.imgur.com/vJ1wZ8V.png", caption="AfyaPlate KE helps you make informed nutritional choices.")
    
    st.info("Select a tool from the sidebar to get started.", icon="👈")


elif app_mode == "🔍 Food Search":
    show_food_search(food_data)

elif app_mode == "🍽️ AI Meal Planner":
    show_meal_planner_ui(food_data)

elif app_mode == "📄 Client Reports":
    show_report_generator()

elif app_mode == "⚙️ Settings":
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
                num_rows_to_display=10,
                use_container_width=True
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
```