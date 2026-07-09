import os
import numpy as np
import pandas as pd
import xgboost as xgb
import mlflow
import mlflow.sklearn
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def train_best_model(data_path, model_dir):
    """Loads engineered features, trains the best tuned XGBoost model, logs with MLflow, and saves locally."""
    print("Loading engineered features...")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Feature file not found at {data_path}")
        
    df = pd.read_csv(data_path, parse_dates=['order_purchase_timestamp'], index_col='order_purchase_timestamp')
    df = df.sort_index()
    
    # Define features and target
    target_col = 'total_sales'
    feature_cols = [col for col in df.columns if col not in [target_col, 'total_items', 'total_orders']]
    
    X = df[feature_cols]
    y = df[target_col]
    
    # Time-series train-test split (Use last 30 days for testing)
    split_date = df.index.max() - pd.Timedelta(days=30)
    X_train, X_test = X[X.index <= split_date], X[X.index > split_date]
    y_train, y_test = y[y.index <= split_date], y[y.index > split_date]
    
    print(f"Training set size: {X_train.shape[0]} days (up to {split_date.strftime('%Y-%m-%d')})")
    print(f"Test set size: {X_test.shape[0]} days (from {(split_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')})")
    
    # Start MLflow run
    mlflow.set_experiment("Sales_Forecasting")
    with mlflow.start_run(run_name="Tuned_XGBoost_Production"):
        # Best tuned hyperparameters from GridSearchCV
        params = {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.05,
            "random_state": 42
        }
        
        print("Training Tuned XGBoost Regressor...")
        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train)
        
        # Evaluate model
        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)
        
        print(f"Test Metrics - MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.2f}")
        
        # Log to MLflow
        mlflow.log_params(params)
        mlflow.log_metrics({"mae": mae, "rmse": rmse, "r2": r2})
        mlflow.sklearn.log_model(model, "xgboost_model", serialization_format="pickle")
        
        # Save model locally for easy API / dashboard loading
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "best_xgboost_model.json")
        model.save_model(model_path)
        print(f"Model saved locally to {model_path}")
        print("MLflow tracking logged successfully.")

if __name__ == "__main__":
    features_file = "data/processed/features_sales.csv"
    output_model_dir = "models"
    
    train_best_model(features_file, output_model_dir)
