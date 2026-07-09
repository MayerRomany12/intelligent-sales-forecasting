from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
# from src.predict import load_model, make_prediction

app = FastAPI(title="Sales Forecasting API", description="API to predict future sales.")

# Placeholder for loaded model
# model = load_model("runs:/<run_id>/random_forest_model")

class SalesRequest(BaseModel):
    # Add your feature fields here based on your trained model
    month: int
    day: int
    holiday_flag: int
    # ... other features ...

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sales Forecasting API!"}

@app.post("/predict")
def predict_sales(request: SalesRequest):
    """Endpoint to predict sales based on input features."""
    # data = pd.DataFrame([request.dict()])
    # prediction = make_prediction(model, data)
    prediction = 1000.0  # Placeholder
    
    return {"forecasted_sales": prediction}
