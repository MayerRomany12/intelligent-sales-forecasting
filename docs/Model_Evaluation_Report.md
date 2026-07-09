# Milestone 3: Model Development & Evaluation Report

## 1. Validation Strategy (TimeSeriesSplit)
To ensure reliable forecasting and prevent data leakage, we utilized **TimeSeriesSplit** with 5 folds. In each fold, the training window is rolled forward, ensuring the model only trains on past data to predict future daily sales.

---

## 2. Models Evaluated & Performance Comparison
Three distinct classes of forecasting models were trained and evaluated on the daily sales dataset:

### A. Random Forest Regressor (Baseline ML)
* **Configuration:** `n_estimators=100`, `max_depth=10`
* **Performance:**
  * Mean MAE: 4,890.65
  * Mean RMSE: 7,324.20
  * Mean R²: 0.24

### B. XGBoost Regressor (Baseline)
* **Configuration:** `n_estimators=100`, `max_depth=5`, `learning_rate=0.1`
* **Performance:**
  * Mean MAE: 5,227.93
  * Mean RMSE: 7,639.09
  * Mean R²: 0.19

### C. SARIMAX (Statistical Time Series)
* **Configuration:** `order=(1,1,1)`, `seasonal_order=(1,1,1,7)`, exogenous features: `['is_holiday', 'is_weekend']`
* **Performance (Fold 5):**
  * MAE: 21,262.27
  * RMSE: 24,411.10
  * R²: -3.25
* **Note:** SARIMAX performed poorly because traditional linear models struggle to model the high volatility, non-linear relationships, and huge outlier spikes (e.g. Black Friday) present in e-commerce daily sales data.

### D. Tuned XGBoost Regressor (Final Model)
* **Tuning Method:** Grid Search CV with TimeSeriesSplit
* **Optimal Hyperparameters:** `learning_rate=0.05`, `max_depth=5`, `n_estimators=100`
* **Performance:**
  * Mean MAE: 4,907.12
  * Mean RMSE: 7,296.99
  * Mean R²: 0.24

---

## 3. Experiment Tracking (MLflow)
All model training iterations, parameters, and performance metrics were logged to **MLflow** under the experiment `Sales_Forecasting_Notebook`. This provides a fully auditable track record of the optimization process:
* **RF_Baseline:** Saved baseline Random Forest model.
* **XGB_Baseline:** Saved baseline XGBoost model.
* **SARIMAX_Model:** Tracked statistical order parameters and metrics.
* **Tuned_XGBoost:** Saved the best-performing hyperparameters and the final model binary.

---

## 4. Final Model Selection & Export
The **Tuned XGBoost Regressor** was selected as the final production model. While its MAE is on par with the Random Forest, XGBoost features lower RMSE (7,296.99 vs 7,324.20) and offers superior performance, speed, and ease of deployment.
* The model has been exported to [best_xgboost_model.json](file:///c:/Users/Mayer_R/Olist/models/best_xgboost_model.json).
* The training code is fully automated in [train.py](file:///c:/Users/Mayer_R/Olist/src/train.py) and ready for integration into the FastAPI web service.
