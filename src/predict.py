import os
import pandas as pd
import numpy as np
import xgboost as xgb
import holidays

def load_prediction_model(model_path="models/best_xgboost_model.json"):

    """Loads the trained XGBoost model from the local path."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found at {model_path}. Please run train.py first.")
    model = xgb.XGBRegressor()
    model.load_model(model_path)
    return model

def prepare_features_for_date(target_date_str, history_path="data/processed/time_series_sales.csv", df_history=None, country="BR"):
    """
    Dynamically generates the full feature vector for a given target date.
    Loads daily historical sales, appends the target date if missing, and calculates 
    time features, holiday flags, lags, and rolling averages.
    """
    target_date = pd.to_datetime(target_date_str)
    
    # Load history if not provided
    if df_history is None:
        df_history = pd.read_csv(history_path, parse_dates=['order_purchase_timestamp'], index_col='order_purchase_timestamp')
        df_history = df_history.sort_index()
    else:
        df_history = df_history.copy()
        
    # If the target date is not in history, append a dummy row for it to calculate features
    if target_date not in df_history.index:
        df_target = pd.DataFrame(index=[target_date], columns=['total_sales', 'total_items', 'total_orders'])
        df_target.fillna(0.0, inplace=True)
        df_combined = pd.concat([df_history, df_target]).sort_index()
    else:
        df_combined = df_history.copy()
        
    # Calculate features on the combined dataset
    # 1. Time features
    df_combined['day_of_week'] = df_combined.index.dayofweek
    df_combined['month'] = df_combined.index.month
    df_combined['quarter'] = df_combined.index.quarter
    df_combined['is_weekend'] = df_combined['day_of_week'].isin([5, 6]).astype(int)
    
    # 2. Holiday flags
    years = df_combined.index.year.unique().tolist()
    country_holidays = holidays.country_holidays(country, years=years)
    df_combined['is_holiday'] = df_combined.index.map(lambda x: x in country_holidays).astype(int)
    
    # 3. Lag features (based on total_sales)
    for lag in [1, 7, 14, 30]:
        df_combined[f'total_sales_lag_{lag}'] = df_combined['total_sales'].shift(lag)
        
    # 4. Rolling features
    for window in [7, 30]:
        df_combined[f'total_sales_rolling_avg_{window}'] = df_combined['total_sales'].rolling(window=window).mean()
        df_combined[f'total_sales_rolling_std_{window}'] = df_combined['total_sales'].rolling(window=window).std()
        
    df_target = df_combined.loc[[target_date]]
    
    # Drop target and count columns
    feature_cols = [col for col in df_target.columns if col not in ['total_sales', 'total_items', 'total_orders']]
    return df_target[feature_cols]

def predict_sales_for_date(target_date_str, model_path="models/best_xgboost_model.json", history_path="data/processed/time_series_sales.csv", df_history=None):
    """Loads the model, prepares features for the target date, and makes a prediction."""
    model = load_prediction_model(model_path)
    features = prepare_features_for_date(target_date_str, history_path=history_path, df_history=df_history)
    
    # Align features column order with the trained model's feature names
    trained_features = model.get_booster().feature_names
    if trained_features:
        features = features[trained_features]
        
    prediction = model.predict(features)[0]
    return max(0.0, float(prediction)) # Ensure non-negative sales

def predict_sales_sequence(start_date_str, days=7, model_path="models/best_xgboost_model.json", history_path="data/processed/time_series_sales.csv"):
    """
    Predicts sales for a sequence of consecutive days starting from start_date_str,
    using recursive forecasting (each prediction is appended to the history for subsequent steps).
    """
    start_date = pd.to_datetime(start_date_str)
    
    # Load base history
    df_history = pd.read_csv(history_path, parse_dates=['order_purchase_timestamp'], index_col='order_purchase_timestamp')
    df_history = df_history.sort_index()
    
    predictions = []
    current_date = start_date
    
    for _ in range(days):
        date_str = current_date.strftime("%Y-%m-%d")
        pred_val = predict_sales_for_date(date_str, model_path=model_path, df_history=df_history)
        
        predictions.append({
            "date": date_str,
            "forecasted_sales": pred_val
        })
        
        # Append the predicted sales to history so it propagates to lag/rolling features
        new_row = pd.DataFrame([[pred_val, 0, 0]], columns=['total_sales', 'total_items', 'total_orders'], index=[current_date])
        df_history = pd.concat([df_history, new_row]).sort_index()
        
        current_date += pd.Timedelta(days=1)
        
    return predictions

if __name__ == "__main__":
    # Test prediction on a sample date (e.g. 2018-08-20, which is near the end of the Olist dataset)
    test_date = "2018-08-20"
    print(f"Testing prediction for {test_date}...")
    try:
        pred = predict_sales_for_date(test_date)
        print(f"Predicted sales for {test_date}: ${pred:,.2f}")
    except Exception as e:
        print(f"Error making prediction: {e}")
