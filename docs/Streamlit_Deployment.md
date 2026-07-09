# Deployment Guide for Streamlit Community Cloud

This guide shows how to deploy the **Streamlit Dashboard** directly to [Streamlit Community Cloud](https://share.streamlit.io/).

---

## 🛠️ Requirements & Setup

Before deploying, ensure you have:
1. Pushed the project repository to GitHub.
2. Created `.streamlit/config.toml` in your repository.
3. Specified all required Python packages (including `streamlit`, `pandas`, `requests`, `plotly`, and `xgboost`) in the root `requirements.txt`.

---

## 🚀 Deployment Steps

1. Visit [Streamlit Community Cloud](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **New app** (or **Deploy an app**).
3. Specify your repository details:
   * **Repository**: select your Olist repository (e.g. `your-username/Olist`)
   * **Branch**: `main` or `master`
   * **Main file path**: `src/dashboard/app.py`
4. Expand the **Advanced settings** menu.
5. In the **Secrets** textbox, define the API URL pointing to your deployed FastAPI server:
   ```toml
   API_URL = "https://olist-sales-api.onrender.com"
   ```
6. Click **Deploy!**
7. Streamlit will provision the container, install packages from `requirements.txt`, read the configuration files, and launch your dashboard.
