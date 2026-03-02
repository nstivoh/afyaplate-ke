# 🇰🇪 AfyaPlate KE

**Kenyan Nutrition Companion built for professionals. Powered by Gemini 2.0 Pro.**

AfyaPlate KE is a premium web application meticulously crafted for Registered Dietitian Nutritionists (RDNs) and healthcare workers in Kenya. It provides instant access to official food composition data, an AI-powered meal planner, and polished client report generation.

![App Screenshot](https://i.imgur.com/gO0A12n.png)

## ✨ Key Features

-   **🤖 Gemini 2.0 Pro**: State-of-the-art AI for culturally-aware, personalized 1-7 day meal plans based on Kenyan dietary patterns.
-   **🔍 Comprehensive Food Search**: Search the complete *Kenya Food Composition Tables (2018)* with English and Swahili support.
-   **📄 Professional PDF Export**: Automatically generate and download branded, print-ready PDF reports for your clients.
-   **💰 Real-time Costing**: Calculate meal costs using editable price estimates for local Kenyan markets.
-   **⚡ High Performance**: Ultra-fast FastAPI backend with an asynchronous Gemini client and a sleek Next.js frontend.

## 🚀 Getting Started

### Prerequisites

-   **Docker & Docker Compose**: Recommended for seamless deployment.
-   **Gemini API Key**: Required for AI-powered generation features.

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
├── backend/                # FastAPI (Python)
│   ├── app/
│   │   ├── api/            # REST Endpoints
│   │   ├── services/       # AI & PDF Services
│   │   └── templates/      # Branded PDF Templates
│   └── main.py
├── frontend/               # Next.js (TypeScript)
│   ├── components/         # Modern UI Components
│   └── public/             # Assets
└── docker-compose.yml
```

## ❤️ Support the Project

If you find AfyaPlate KE useful in your practice, please consider supporting its development.

-   [⭐ **Star the repository on GitHub**](https://github.com/nstivoh/afyaplate-ke)
-   [❤️ **Sponsor development**](https://github.com/sponsors/nstivoh)

---
*Built with passion in Nairobi.*