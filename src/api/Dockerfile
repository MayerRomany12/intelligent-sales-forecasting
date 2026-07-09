# Use a Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    MODEL_PATH=Models/best_xgboost_model.json

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code, model, and processed data
COPY src/ /app/src/
COPY Models/ /app/Models/
COPY data/processed/ /app/data/processed/

# Expose the API port
EXPOSE 8000

# Command to run the application using uvicorn with exec for signal propagation
CMD ["sh", "-c", "exec python -m uvicorn src.api.app:app --host $HOST --port $PORT --workers ${WEB_CONCURRENCY:-1}"]
