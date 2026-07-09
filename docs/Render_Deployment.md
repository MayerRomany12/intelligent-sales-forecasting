# Deployment Guide for Render

This guide describes how to deploy the **FastAPI Backend** and **Streamlit Dashboard** to [Render](https://render.com) using both the Render Dashboard interface and the Blueprint infrastructure-as-code configuration.

---

## 🏗️ Option A: Deployment using Render Blueprints (Recommended)

Render Blueprints allow you to configure all services in a single file (`render.yaml`) and sync it with your GitHub repository.

### Steps:
1. Push your repository (including `render.yaml`) to GitHub.
2. Sign in to your [Render Dashboard](https://dashboard.render.com).
3. Click on **New** -> **Blueprint**.
4. Connect your GitHub repository.
5. Render will parse the `render.yaml` and prompt you to create the services:
   * **olist-sales-api** (FastAPI backend built from Dockerfile)
   * **olist-sales-dashboard** (Streamlit dashboard built from Dockerfile)
6. Once deployed, get your API service URL (e.g. `https://olist-sales-api.onrender.com`).
7. Update the `API_URL` environment variable in the dashboard service settings with your API URL.

---

## 🖥️ Option B: Manual Deployment via Render Dashboard

If you prefer deploying services manually through the dashboard UI:

### 1. Deploy the FastAPI Backend (Web Service)
1. In Render Dashboard, click **New** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the following parameters:
   * **Name**: `olist-sales-api`
   * **Language**: `Docker`
   * **Docker Build Context**: `.`
   * **Dockerfile Path**: `src/api/Dockerfile`
   * **Instance Type**: `Free`
4. Add the following Environment Variables in the **Environment** tab:
   * `PORT`: `10000`
   * `MODEL_PATH`: `Models/best_xgboost_model.json`
   * `CORS_ORIGINS`: `*` (or your frontend URLs)
5. Click **Deploy Web Service**.

### 2. Deploy the Streamlit Dashboard (Web Service)
1. In Render Dashboard, click **New** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the following parameters:
   * **Name**: `olist-sales-dashboard`
   * **Language**: `Docker`
   * **Docker Build Context**: `.`
   * **Dockerfile Path**: `src/dashboard/Dockerfile`
   * **Instance Type**: `Free`
4. Add the following Environment Variables in the **Environment** tab:
   * `PORT`: `8501`
   * `API_URL`: `https://olist-sales-api.onrender.com` (use your actual deployed API URL)
5. Click **Deploy Web Service**.
