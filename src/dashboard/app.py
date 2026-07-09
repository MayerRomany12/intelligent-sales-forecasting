import streamlit as st

import pandas as pd
import requests

st.title("Sales Forecasting Dashboard")
st.write("This dashboard displays the sales forecast for the upcoming period.")

# Sidebar for inputs
st.sidebar.header("Input Features")
month = st.sidebar.slider("Month", 1, 12, 1)
day = st.sidebar.slider("Day", 1, 31, 1)
holiday_flag = st.sidebar.selectbox("Is Holiday?", [0, 1])

if st.button("Predict Sales"):
    # Prepare payload for API
    payload = {
        "month": month,
        "day": day,
        "holiday_flag": holiday_flag
    }
    
    try:
        # Call the FastAPI service (assuming it runs on port 8000)
        response = requests.post("http://localhost:8000/predict", json=payload)
        
        if response.status_code == 200:
            prediction = response.json()["forecasted_sales"]
            st.success(f"Forecasted Sales: ${prediction:,.2f}")
        else:
            st.error("Error from API")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Make sure the FastAPI app is running.")
