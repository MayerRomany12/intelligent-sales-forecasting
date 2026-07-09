# Docker Deployment & Local Running Guide

This guide provides step-by-step instructions on how to build, run, and manage the Olist Sales Forecasting project using Docker and Docker Compose.

---

## 🛠️ Prerequisites

Before you start, make sure you have the following installed on your machine:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop)

---

## 🚀 Running the Full Stack with Docker Compose

We have prepared a `docker-compose.yml` file that orchestrates the following three services:
1. **Backend (FastAPI)**: Serves the ML prediction endpoints on port `8000`.
2. **Dashboard (Streamlit)**: Shows interactive charts and lets you query the backend on port `8501`.
3. **Frontend (React Client)**: A lightweight responsive user interface running on port `3000`.

### 1. Configure the Environment
Ensure that `.env` is created. You can copy the example file:
```bash
cp .env.example .env
```
*(By default, the docker compose configuration reads values directly from this file or uses defaults).*

### 2. Build and Start the Services
Run the following command in the root directory:
```bash
docker-compose up --build -d
```
This command:
* Builds the Docker images for all three services (`backend`, `dashboard`, `frontend`).
* Starts them in detached mode (`-d`).
* Binds local data and model directories into the backend container so updates persist.

### 3. Verify Deployed Services
Check that all containers are healthy and running:
```bash
docker-compose ps
```
You can access the services in your browser:
* **React Frontend**: [http://localhost:3000](http://localhost:3000)
* **Streamlit Dashboard**: [http://localhost:8501](http://localhost:8501)
* **FastAPI documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **API Health Check**: [http://localhost:8000/health](http://localhost:8000/health) (should respond with `{"status":"healthy","model_loaded":true}`)

---

## 🐳 Running Services Separately (Docker CLI)

If you prefer building and running images individually without Docker Compose, follow these steps:

### 1. Build and Run the FastAPI Backend
```bash
# Build
docker build -t olist-backend -f src/api/Dockerfile .

# Run
docker run -d -p 8000:8000 --name olist_backend_container \
  -e PORT=8000 -e HOST=0.0.0.0 olist-backend
```

### 2. Build and Run the Streamlit Dashboard
```bash
# Build
docker build -t olist-dashboard -f src/dashboard/Dockerfile .

# Run (connect to backend running on your host machine)
docker run -d -p 8501:8501 --name olist_dashboard_container \
  -e API_URL=http://localhost:8000 olist-dashboard
```

### 3. Build and Run the React Frontend
```bash
# Build (pass backend API URL as argument)
docker build -t olist-frontend --build-arg VITE_API_URL=http://localhost:8000 ./frontend

# Run
docker run -d -p 3000:80 --name olist_frontend_container olist-frontend
```

---

## 🛑 Stopping and Cleaning Up

To stop the services and remove containers, networks, and volumes:
```bash
docker-compose down
```
To remove built images as well:
```bash
docker-compose down --rmi all
```
