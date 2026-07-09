# Environment Variables Configuration Guide

This document describes the environment variables used by the Olist Sales Forecasting services and how to configure them for local and production deployment.

---

## 📋 Available Environment Variables

| Variable Name | Targeted Service | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `PORT` | Backend / Dashboard | `8000` / `8501` | The network port the service listens to. |
| `HOST` | Backend / Dashboard | `0.0.0.0` | The network interface address bind configuration. |
| `MODEL_PATH` | Backend (FastAPI) | `Models/best_xgboost_model.json` | Path to the trained XGBoost json model file. |
| `CORS_ORIGINS` | Backend (FastAPI) | `*` | Comma-separated list of client origins allowed to access the API. |
| `API_URL` | Streamlit Dashboard | `http://localhost:8000` | Target URL of the FastAPI backend API server. |
| `VITE_API_URL` | React Frontend | `http://localhost:8000` | Target URL of the FastAPI backend API server (built-in). |

---

## 🛠️ Configuration Methods

### 1. Local Development (`.env` file)
Copy `.env.example` to `.env` in the root folder. Docker Compose reads values from this file automatically during runtime:
```bash
cp .env.example .env
```

### 2. Docker Compose
You can adjust values directly inside `docker-compose.yml` under the `environment` keys.

### 3. Vercel (React Frontend)
In Vercel project settings, go to **Environment Variables** and add `VITE_API_URL`. This variable must be set before triggering the build process since Vite compiles variables with the client-side bundle.

### 4. Render (Backend & Streamlit)
In the Render Web Service dashboard, go to the **Environment** tab and add the variables (`PORT`, `MODEL_PATH`, `CORS_ORIGINS`, `API_URL`).
