# AfyaPlate KE Deployment Guide

This document provides instructions for deploying the AfyaPlate KE application, which consists of a Next.js frontend and a FastAPI backend.

## Frontend (Next.js) - Deploying to Vercel

Vercel is the recommended platform for deploying the Next.js frontend due to its seamless integration and performance features.

1.  **Sign up and Connect Your Git Repository:**
    *   Create an account on [Vercel](https://vercel.com).
    *   Connect your Git provider (GitHub, GitLab, Bitbucket) and import the repository containing this codebase.

2.  **Configure Your Project:**
    *   Vercel will automatically detect that you are deploying a Next.js application.
    *   The **Root Directory** should be set to `frontend`.
    *   The build and output settings will be configured automatically.

3.  **Add Environment Variables:**
    *   You need to tell the frontend where to find your deployed backend API.
    *   Go to your project's "Settings" -> "Environment Variables".
    *   Add the following variable:
        *   `NEXT_PUBLIC_API_BASE_URL`: The full URL of your deployed FastAPI backend (e.g., `https://afyaplate-backend-production.up.railway.app/api/v1`).

4.  **Deploy:**
    *   Click the "Deploy" button. Vercel will build and deploy your frontend. Subsequent pushes to your connected Git branch will trigger automatic deployments.

## Backend (FastAPI) - Deploying to Railway

Railway is a great choice for the FastAPI backend due to its simplicity and integrated database services.

1.  **Sign up and Create a Project:**
    *   Create an account on [Railway](https://railway.app).
    *   Create a new project and link it to your Git repository.

2.  **Configure the FastAPI Service:**
    *   When adding a new service from your repository, Railway might ask for the root directory. Point it to the `backend` directory.
    *   Railway uses a `railway.toml` file or Procfile for configuration. Let's use build and start commands.
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3.  **Add a Redis Service:**
    *   The backend requires a Redis instance for caching.
    *   In your Railway project, click "+ New" -> "Database" -> "Redis".
    *   Railway will automatically provision a Redis database and inject the connection URL as an environment variable (`REDIS_URL`) into your FastAPI service. The application is already configured to use this environment variable.

4.  **Add Environment Variables:**
    *   Go to your backend service's "Variables" tab.
    *   The `REDIS_URL` will already be present.
    *   You may need to configure `BACKEND_CORS_ORIGINS` to allow requests from your deployed Vercel frontend URL.
        *   `BACKEND_CORS_ORIGINS`: `["https://your-vercel-frontend-url.vercel.app"]` (replace with your actual frontend URL).

5.  **Deploy:**
    *   Railway will automatically deploy when you push changes to your repository. Check the deployment logs for any build or runtime errors.

---
This setup provides a robust, scalable, and performant architecture for the full-stack AfyaPlate KE application.
