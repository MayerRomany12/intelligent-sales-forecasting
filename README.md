# Sales Forecasting and Demand Prediction

This repository contains the end-to-end Machine Learning pipeline for predicting future sales using the Brazilian E-Commerce dataset.

## Milestones

1. **Data Collection, Exploration, and Preprocessing**: See `notebooks/01_data_exploration_and_preprocessing.ipynb`.
2. **Advanced Data Analysis and Feature Engineering**: See `notebooks/02_advanced_analysis_and_feature_engineering.ipynb`.
3. **Machine Learning Model Development**: See `notebooks/03_model_development_and_optimization.ipynb`.
4. **MLOps, Deployment, and Monitoring**:
   - `src/train.py` & `src/predict.py`: Model scripts tracking with MLflow.
   - `api/app.py`: FastAPI backend to serve the model.
   - `dashboard/app.py`: Streamlit dashboard for interactive prediction.

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Download the data from Kaggle (make sure `kaggle.json` is configured):
   ```bash
   python download_data.py
   ```
3. Run the API (from root directory):
   ```bash
   uvicorn api.app:app --reload
   ```
4. Run the Dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```
