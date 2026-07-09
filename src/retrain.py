import os
import numpy as np
import pandas as pd
import xgboost as xgb
import mlflow
import mlflow.sklearn
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.feature_engineering import feature_engineering_pipeline

def evaluate_model(model, X_test, y_test):
    """Evaluates a model and returns MAE, RMSE, and R2 score."""
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    return mae, rmse, r2

def check_and_retrain(
    input_ts_file="data/processed/time_series_sales.csv",
    features_file="data/processed/features_sales.csv",
    model_dir="Models"
):
    """
    Runs feature engineering, trains a new XGBoost model,
    compares its MAE with the current best model,
    and updates the production model if the new one is more accurate.
    """
    print("Step 1: Running Feature Engineering Pipeline...")
    if not os.path.exists(input_ts_file):
        raise FileNotFoundError(f"Historical time series not found at {input_ts_file}")
    
    # Refresh feature file
    feature_engineering_pipeline(input_ts_file, features_file)
    
    print("Step 2: Loading engineered features...")
    df = pd.read_csv(features_file, parse_dates=['order_purchase_timestamp'], index_col='order_purchase_timestamp')
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
    
    print(f"Dataset Split Details:")
    print(f" - Train set: {X_train.shape[0]} days (up to {split_date.strftime('%Y-%m-%d')})")
    print(f" - Test set: {X_test.shape[0]} days (from {(split_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')})")
    
    # Check if a model already exists to compare against
    model_path = os.path.join(model_dir, "best_xgboost_model.json")
    if not os.path.exists(model_path):
        # Fallback to lowercase models
        model_path = "models/best_xgboost_model.json"
        
    old_model = None
    old_mae = float('inf')
    old_rmse = float('inf')
    old_r2 = -float('inf')
    
    if os.path.exists(model_path):
        print(f"Loading current best model from {model_path} for performance baseline...")
        try:
            old_model = xgb.XGBRegressor()
            old_model.load_model(model_path)
            
            # Align features order
            trained_features = old_model.get_booster().feature_names
            if trained_features:
                X_test_old = X_test[trained_features]
            else:
                X_test_old = X_test
                
            old_mae, old_rmse, old_r2 = evaluate_model(old_model, X_test_old, y_test)
            print(f"Current Model Metrics - MAE: {old_mae:.2f}, RMSE: {old_rmse:.2f}, R2: {old_r2:.2f}")
        except Exception as e:
            print(f"Warning: Could not evaluate existing model: {e}. A new model will be trained and set as production.")
    else:
        print("No pre-existing model found. Training a new production model...")

    # Start MLflow run to log retraining process
    mlflow.set_experiment("Sales_Forecasting_Retraining")
    with mlflow.start_run(run_name="Automated_Retraining_Run"):
        params = {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.05,
            "random_state": 42
        }
        
        print("Training new XGBoost Regressor model...")
        new_model = xgb.XGBRegressor(**params)
        new_model.fit(X_train, y_train)
        
        new_mae, new_rmse, new_r2 = evaluate_model(new_model, X_test, y_test)
        print(f"New Model Metrics - MAE: {new_mae:.2f}, RMSE: {new_rmse:.2f}, R2: {new_r2:.2f}")
        
        # Log new model metrics to MLflow
        mlflow.log_params(params)
        mlflow.log_metrics({"mae": new_mae, "rmse": new_rmse, "r2": new_r2})
        mlflow.sklearn.log_model(new_model, "xgboost_model_retrained", serialization_format="pickle")
        
        # Compare metrics: lower MAE is better
        if new_mae < old_mae:
            print("SUCCESS: The new model outperforms the current production model.")
            print(f"Improvement in MAE: {old_mae - new_mae:.2f} (${old_mae:.2f} -> ${new_mae:.2f})")
            
            # Save the new model to Models (and models as fallback)
            os.makedirs(model_dir, exist_ok=True)
            new_model_path = os.path.join(model_dir, "best_xgboost_model.json")
            new_model.save_model(new_model_path)
            print(f"New model saved locally to {new_model_path}")
            
            # If lowercase models dir exists, save there too
            if os.path.exists("models"):
                new_model.save_model("models/best_xgboost_model.json")
                
            mlflow.log_param("deployed", True)
            return True
        else:
            print("ALERT: The new model does NOT perform better than the current model.")
            print(f"MAE did not decrease: Current MAE = ${old_mae:.2f}, New MAE = ${new_mae:.2f}")
            print("Keeping the current production model.")
            
            mlflow.log_param("deployed", False)
            return False

if __name__ == "__main__":
    check_and_retrain()
