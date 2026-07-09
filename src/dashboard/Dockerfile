# Use a Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8501 \
    HOST=0.0.0.0 \
    API_URL=http://localhost:8000

# Set working directory in container
WORKDIR /app

# Copy requirements from root and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code, model, and processed data
COPY src/ /app/src/
COPY Models/ /app/Models/
COPY data/processed/ /app/data/processed/
COPY .streamlit/ /app/.streamlit/

# Expose the dashboard port
EXPOSE 8501

# Command to run Streamlit with exec for signal propagation
CMD ["sh", "-c", "exec python -m streamlit run src/dashboard/app.py --server.port $PORT --server.address $HOST"]
