# 🇰🇪 AfyaPlate KE

**Your all-in-one, AI-powered nutrition tool for Kenyan healthcare professionals.**

AfyaPlate KE is a modern web application designed for Registered Dietitian Nutritionists (RDNs) and healthcare workers in Kenya. It provides instant access to food composition data, an AI-powered meal planner, and professional report generation.

![App Screenshot](https://i.imgur.com/gO0A12n.png)

## ✨ Key Features

-   **🤖 Gemini 2.0 Integration**: Leverage the latest Google GenAI models for culturally-aware, personalized meal plans.
-   **🔍 Comprehensive Food Search**: Instantly search the complete *Kenya Food Composition Tables (2018)*.
-   **📄 PDF Export**: Generate and download print-ready PDF reports for your clients with a single click.
-   **💰 Food Costing**: Calculate meal costs using editable price estimates for local Kenyan markets.
-   **⚡ Modern Architecture**: Built with FastAPI (Backend) and Next.js (Frontend) for speed and reliability.

## 🚀 Getting Started

### Prerequisites

-   **Docker & Docker Compose**: The easiest way to run the entire stack.
-   **Gemini API Key**: Required for the AI Meal Planner features.

### Installation & Run

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/nstivoh/afyaplate-ke.git
    cd afyaplate-ke
    ```

2.  **Launch with Docker:**
    ```bash
    docker compose up -d --build
    ```

3.  **Access the App:**
    -   **Frontend**: [http://localhost:3000](http://localhost:3000)
    -   **Backend API**: [http://localhost:8000](http://localhost:8000)

## 📁 Project Structure

```
afyaplate-ke/
├── backend/                # FastAPI Application
│   ├── app/
│   │   ├── api/            # API Endpoints
│   │   ├── services/       # LLM & PDF logic
│   │   └── templates/      # PDF HTML templates
│   └── main.py
├── frontend/               # Next.js Application (TypeScript)
│   ├── components/         # React Components
│   ├── pages/
│   └── public/
└── docker-compose.yml
```

## ❤️ Support the Project

If you find AfyaPlate KE useful, please consider supporting its development:

-   [⭐ **Star the repository on GitHub**](https://github.com/nstivoh/afyaplate-ke)
-   [❤️ **Sponsor development**](https://github.com/sponsors/nstivoh)

---
*Built with passion in Nairobi.*