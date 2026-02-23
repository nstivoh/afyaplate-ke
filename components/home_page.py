# filepath: components/home_page.py
import streamlit as st

def show_home_page():
    """
    Renders a custom, modern home page using st.components.v1.html.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

            :root {
                --primary-color: #008000; /* Green */
                --secondary-color: #333333;
                --background-color: #F8F9FA;
                --card-background: #FFFFFF;
                --card-shadow: 0 4px 8px rgba(0,0,0,0.05);
            }

            body {
                font-family: 'Inter', sans-serif;
                background-color: var(--background-color);
                color: var(--secondary-color);
                margin: 0;
                padding: 2rem;
            }

            .container {
                max-width: 900px;
                margin: auto;
            }

            .header {
                text-align: center;
                margin-bottom: 3rem;
            }

            .header h1 {
                font-size: 3rem;
                font-weight: 700;
                color: var(--primary-color);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }

            .header p {
                font-size: 1.2rem;
                color: #555;
            }
            
            .main-cta {
                display: inline-block;
                background-color: var(--primary-color);
                color: white;
                padding: 1rem 2rem;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                font-size: 1.1rem;
                transition: transform 0.2s, box-shadow 0.2s;
                margin-top: 1rem;
            }

            .main-cta:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0, 128, 0, 0.2);
            }

            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-top: 3rem;
            }

            .feature-card {
                background: var(--card-background);
                border-radius: 12px;
                padding: 2rem;
                box-shadow: var(--card-shadow);
                border: 1px solid #eee;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .feature-card:hover {
                 transform: translateY(-5px);
                 box-shadow: 0 8px 16px rgba(0,0,0,0.08);
            }

            .feature-card h3 {
                font-size: 1.3rem;
                font-weight: 600;
                margin-top: 0;
                color: var(--primary-color);
            }
            
            .feature-card p {
                font-size: 0.95rem;
                line-height: 1.6;
            }

        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><span style="font-size: 3.5rem;">🇰🇪</span> AfyaPlate KE</h1>
                <p>Your all-in-one nutrition tool, designed for Kenya.</p>
                <a href="#" class="main-cta">Start Planning Meals</a>
            </div>

            <div class="features-grid">
                <div class="feature-card">
                    <h3>🔍 Food Search</h3>
                    <p>Instantly search the comprehensive Kenya Food Composition Tables (2018) for detailed nutrient information.</p>
                </div>
                <div class="feature-card">
                    <h3>🍽️ Automated Meal Planner</h3>
                    <p>Generate personalized, culturally-aware meal plans using a powerful planning service.</p>
                </div>
                <div class="feature-card">
                    <h3>📄 Client Reports</h3>
                    <p>Create professional, print-ready PDF reports for your clients, complete with shopping lists.</p>
                </div>
                <div class="feature-card">
                    <h3>⚙️ Fully Customizable</h3>
                    <p>Edit food prices, manage client data, and configure the planner to fit your needs.</p>
                </div>
                <div class="feature-card">
                    <h3>🔒 Privacy-First</h3>
                    <p>All your data stays on your computer. With the API-based planner, only anonymized requests are sent.</p>
                </div>
                 <div class="feature-card">
                    <h3>🚀 Modern & Fast</h3>
                    <p>Built with a responsive, modern interface to ensure a smooth and intuitive user experience.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    st.components.v1.html(html_content, height=800, scrolling=True)
