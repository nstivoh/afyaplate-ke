# 🇰🇪 AfyaPlate KE

**Your all-in-one, offline-first, AI-powered nutrition tool for Kenyan healthcare professionals.**

AfyaPlate KE is a Streamlit application meticulously crafted for Registered Dietitian Nutritionists (RDNs) and other healthcare workers in Kenya. It provides instant access to food composition data, an AI-powered meal planner, and client report generation, all while running completely offline to ensure 100% data privacy.

This tool is built by a Kenyan RDN, for Kenyan RDNs.

![App Screenshot](https://i.imgur.com/gO0A12n.png)

## ✨ Key Features

-   **🔒 100% Offline & Private**: After the initial setup, no internet connection is required. All client data is stored locally on your machine.
-   **🔍 Comprehensive Food Search**: Instantly search the complete *Kenya Food Composition Tables (2018)*. Filter by food group, and search by English or Swahili names.
-   **🤖 AI Meal Planner**: Leverage a local AI model (Ollama) to generate culturally-aware, personalized 1-7 day meal plans based on client profiles (age, condition, budget, etc.).
-   **📄 Professional PDF Reports**: Automatically generate and download print-ready PDF reports for your clients, complete with your professional branding.
-   **💰 Recipe & Meal Costing**: Use a built-in, editable price list for common Nairobi foods (2026 estimates) to calculate meal costs.
-   **🇰🇪 For Kenya, By Kenya**: Designed with Kenyan nutritional needs, common conditions, and cultural food practices in mind.

## 🚀 Getting Started

### Prerequisites

1.  **Python 3.8+**: Make sure you have a modern version of Python installed.
2.  **System Dependencies**: This tool requires `ghostscript` and `poppler-utils` for PDF processing.
3.  **Ollama**: You must have [Ollama](https://ollama.ai/) installed and running for the AI Meal Planner to work.

### Installation

1.  **Install System Dependencies (Debian/Ubuntu/Parrot Sec OS):**
    ```bash
    sudo apt update && sudo apt install ghostscript poppler-utils -y
    ```

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/nstivoh/afyaplate-ke.git
    cd afyaplate-ke
    ```

3.  **Set up a Python Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Install Required Python Packages:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Download the AI Model:**
    Pull the `deepseekcoderafya` model (or your preferred compatible model) for the AI planner.
    ```bash
    ollama pull deepseekcoderafya
    ```

### Running the Application

1.  **Ensure the Ollama server is running in a separate terminal:**
    ```bash
    ollama serve
    ```

2.  **Run the Streamlit App:**
    ```bash
    streamlit run app.py
    ```
    Your browser will open with the AfyaPlate KE application running locally.

### First-Time Setup in the App

The first time you run the app, the food database will be empty.
1.  Navigate to the **⚙️ Settings** tab.
2.  In the "Extract Food Data from PDF" section, click the **"Start PDF Extraction"** button.
3.  This process will take **1-3 minutes**. Once complete, the app is fully functional.

## Project Structure

```
afyaplate-ke/
├── app.py                  # Main Streamlit entrypoint
├── requirements.txt
├── .streamlit/config.toml  # Custom theme file
├── data/
│   ├── KFCT_2018.pdf       # Source data
│   ├── kfct_clean.csv      # Processed data (generated)
│   ├── prices_nairobi_2026.json
│   └── clients/            # Local JSON client files are saved here
├── core/                   # Backend logic
│   ├── data_loader.py
│   ├── llm_meal_planner.py
│   ├── pdf_extractor.py
│   └── pdf_report.py
├── components/             # Frontend UI modules
│   ├── food_search.py
│   ├── meal_planner_ui.py
│   └── report_generator.py
└── README.md
```

## ❤️ Support the Project

If you find AfyaPlate KE useful in your practice, please consider supporting its development. Your support helps maintain the project and add new features.

-   [⭐ **Star the repository on GitHub**](https://github.com/nstivoh/afyaplate-ke)
-   [❤️ **Sponsor me on GitHub**](https://github.com/sponsors/nstivoh)

---
*Built with passion in Nairobi on Parrot Security OS.*