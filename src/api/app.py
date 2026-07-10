from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import datetime
import os
from src.predict import predict_sales_for_date, predict_sales_sequence, load_prediction_model
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("sales-api")

# Pre-load model at startup
global_model = None
try:
    model_path = os.getenv("MODEL_PATH", "Models/best_xgboost_model.json")
    if not os.path.exists(model_path):
        if os.path.exists("models/best_xgboost_model.json"):
            model_path = "models/best_xgboost_model.json"
        elif os.path.exists("Models/best_xgboost_model.json"):
            model_path = "Models/best_xgboost_model.json"
            
    if os.path.exists(model_path):
        global_model = load_prediction_model(model_path)
        logger.info(f"Loaded XGBoost model successfully from {model_path}")
    else:
        logger.warning(f"XGBoost model file not found at {model_path} during startup.")
except Exception as e:
    logger.error(f"Error loading model at startup: {e}")

app = FastAPI(
    title="Sales Forecasting API",
    description="FastAPI service for Olist sales prediction and recursive sequence forecasting.",
    version="1.0.0"
)

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SinglePredictionRequest(BaseModel):
    date: str = Field(..., description="Target date in YYYY-MM-DD format", example="2018-08-20")

    class Config:
        schema_extra = {
            "example": {
                "date": "2018-08-20"
            }
        }

class SequencePredictionRequest(BaseModel):
    start_date: str = Field(..., description="Start date of sequence in YYYY-MM-DD format", example="2018-08-20")
    days: int = Field(7, description="Number of days to forecast", ge=1, le=30, example=7)

    class Config:
        schema_extra = {
            "example": {
                "start_date": "2018-08-20",
                "days": 7
            }
        }

def validate_date_str(date_str: str):
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format: '{date_str}'. Use YYYY-MM-DD format."
        )

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Sales Forecasting API!",
        "version": "1.1.0-recursive",
        "endpoints": {
            "/health": "GET - Check API status",
            "/predict": "POST - Predict sales for a single date",
            "/predict/sequence": "POST - Predict sales for a sequence of days starting from a date"
        }
    }

@app.get("/health")
def health_check():
    """Simple endpoint to verify server health and model availability."""
    global global_model
    if global_model is not None:
        return {"status": "healthy", "model_loaded": True}
        
    model_path = os.getenv("MODEL_PATH", "Models/best_xgboost_model.json")
    model_exists = os.path.exists(model_path)
    if not model_exists:
        model_exists = os.path.exists("models/best_xgboost_model.json") or os.path.exists("Models/best_xgboost_model.json")
        
    if model_exists:
        try:
            if not os.path.exists(model_path):
                if os.path.exists("models/best_xgboost_model.json"):
                    model_path = "models/best_xgboost_model.json"
                elif os.path.exists("Models/best_xgboost_model.json"):
                    model_path = "Models/best_xgboost_model.json"
            global_model = load_prediction_model(model_path)
            return {"status": "healthy", "model_loaded": True}
        except Exception as e:
            return {"status": "degraded", "detail": f"Failed to load model: {str(e)}", "model_loaded": False}
    else:
        return {"status": "degraded", "detail": "Trained model not found at path.", "model_loaded": False}

@app.post("/predict")
def predict_sales(request: SinglePredictionRequest):
    """Predict sales for a single target date."""
    validate_date_str(request.date)
    try:
        model_path = os.getenv("MODEL_PATH", "Models/best_xgboost_model.json")
        if not os.path.exists(model_path):
            if os.path.exists("models/best_xgboost_model.json"):
                model_path = "models/best_xgboost_model.json"
            elif os.path.exists("Models/best_xgboost_model.json"):
                model_path = "Models/best_xgboost_model.json"
            
        prediction = predict_sales_for_date(request.date, model_path=model_path, model=global_model)
        return {
            "date": request.date,
            "forecasted_sales": round(prediction, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/sequence")
def predict_sequence(request: SequencePredictionRequest):
    """Predict sales for a sequence of days starting from start_date."""
    validate_date_str(request.start_date)
    try:
        model_path = os.getenv("MODEL_PATH", "Models/best_xgboost_model.json")
        if not os.path.exists(model_path):
            if os.path.exists("models/best_xgboost_model.json"):
                model_path = "models/best_xgboost_model.json"
            elif os.path.exists("Models/best_xgboost_model.json"):
                model_path = "Models/best_xgboost_model.json"
            
        predictions = predict_sales_sequence(request.start_date, days=request.days, model_path=model_path, model=global_model)
        # Round predictions
        for pred in predictions:
            pred["forecasted_sales"] = round(pred["forecasted_sales"], 2)
            
        return {
            "start_date": request.start_date,
            "days": request.days,
            "predictions": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sequence prediction error: {str(e)}")
