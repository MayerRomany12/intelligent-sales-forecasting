# Milestone 2: Advanced Data Analysis & Feature Engineering Summary

## 1. Time Series Analysis & Stationarity
Before model training, we conducted statistical checks to evaluate if the daily sales series is suitable for time series forecasting.

* **Augmented Dickey-Fuller (ADF) Test:**
  * **Null Hypothesis ($H_0$):** The series has a unit root (is non-stationary).
  * **Test Statistic:** -3.14  
  * **p-value:** 0.023 (< 0.05)  
  * **Conclusion:** We reject the null hypothesis. The series is **stationary** at a 5% significance level, meaning its statistical properties (mean, variance) remain relatively stable over time, making it suitable for forecasting without additional differencing.

---

## 2. Feature Engineering & Descriptions
To enable machine learning algorithms (which do not implicitly understand time order) to predict sales, we extracted the following structured features:

### A. Calendar & Time Features
* `day_of_week`: Day index (0 = Monday, 6 = Sunday) to capture weekly cycles.
* `month`: Month of the year (1 to 12) to capture seasonal consumer behaviors (e.g. year-end holiday surges).
* `quarter`: Quarter of the year (1 to 4).
* `is_weekend`: Binary flag (1 if Saturday/Sunday, 0 otherwise).

### B. External Exogenous Features
* `is_holiday`: Binary flag (1 if the date matches a national holiday in Brazil, 0 otherwise). Extracted using the Python library `holidays` for Brazil. Public holidays generally show a sharp drop in daily purchasing volume.

### C. Lag Features (Autoregressive Components)
* `total_sales_lag_1`: Sales from 1 day prior (captures day-to-day momentum).
* `total_sales_lag_7`: Sales from 1 week prior (captures weekly patterns).
* `total_sales_lag_14`: Sales from 2 weeks prior.
* `total_sales_lag_30`: Sales from 30 days prior (captures monthly cycles).

### D. Rolling Window Statistics
* `total_sales_rolling_avg_7` & `total_sales_rolling_std_7`: The 7-day rolling mean and standard deviation. Captures the short-term trend and current volatility.
* `total_sales_rolling_avg_30` & `total_sales_rolling_std_30`: The 30-day rolling mean and standard deviation. Captures the medium-term market growth and trend smoothing.

---

## 3. Correlation Analysis & Insights
* Daily sales show a strong positive correlation with `total_sales_rolling_avg_7` ($r \approx 0.74$) and `total_sales_lag_7` ($r \approx 0.61$). This confirms that the weekly seasonality is a major driver of daily sales.
* Weekend flags (`is_weekend`) show a negative correlation with sales, indicating that Brazilian e-commerce buyers are less active during weekends than during weekdays.

---

## 4. Final Engineered Dataset
The resulting dataset containing all engineered features for the 700 days of history is saved at:
* [features_sales.csv](file:///c:/Users/Mayer_R/Olist/data/processed/features_sales.csv)
