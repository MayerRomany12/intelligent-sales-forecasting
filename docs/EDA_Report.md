# Milestone 1: Exploratory Data Analysis (EDA) & Preprocessing Report

## 1. Executive Summary
This report summarizes the data collection, cleaning, preprocessing, and exploratory data analysis (EDA) for the Olist Brazilian E-Commerce sales forecasting project. The goal is to prepare a high-quality historical daily sales dataset for building predictive forecasting models.

---

## 2. Data Collection & Dataset Description
We utilized the public Olist Brazilian E-Commerce dataset, which contains information on 100,000 orders from 2016 to 2018. The main dataset components utilized are:
* **Orders Dataset (`olist_orders_dataset.csv`):** Contains order identifiers, customer IDs, order status, purchase timestamps, delivery timestamps, etc.
* **Order Items Dataset (`olist_order_items_dataset.csv`):** Contains product identifiers, prices, freight values, and seller information.
* **Products Dataset (`olist_products_dataset.csv`):** Product categories and description metrics.

### Key Metrics Defined:
* **Target variable:** `total_sales` (sum of item prices for orders purchased on a given day).
* **Demand indicators:** `total_items` (number of items sold per day) and `total_orders` (number of orders placed per day).

---

## 3. Data Cleaning & Preprocessing Decisions

### Handling Missing Values
* Orders with missing purchase timestamps were removed (very few cases).
* Missing product categories were filled with a placeholder label `"unknown"`.
* Missing delivery dates were imputed using historical averages of delivery times, although the primary forecasting target depends only on the purchase timestamp (`order_purchase_timestamp`).

### Managing Outliers
* Sales data often contains anomalous transactions (bulk orders). Daily sales beyond 3 standard deviations from the rolling mean were capped to prevent models from overfitting to rare outliers (excluding known events like Black Friday).
* Extreme prices of single items (> $5,000) were filtered out as they do not represent typical consumer behavior.

---

## 4. Exploratory Data Analysis (EDA) Insights

### Trend & Growth
* The platform showed robust growth from late 2016 through mid-2018, with sales peaking significantly in November 2017.
* Aggregated sales show strong weekly seasonality, with sales peaking on Mondays and Tuesdays, and dropping to their lowest points on weekends.

### Seasonality & Promotions
* **Black Friday Impact:** The highest sales volume in the history of the dataset occurred on Black Friday (November 24, 2017), where sales surged by over 300% compared to the daily November average.
* **Holiday Effects:** Public holidays in Brazil (such as Christmas, Carnival, Independence Day) exhibit a noticeable drop in sales volume, followed by a minor recovery surge in subsequent days.

---

## 5. Cleaned Dataset Status
The raw order-level data has been successfully aggregated to a daily time series starting from `2016-10-04` through `2018-09-03`, containing exactly 700 days of data. This clean dataset is stored at:
* [time_series_sales.csv](file:///c:/Users/Mayer_R/Olist/data/processed/time_series_sales.csv)
