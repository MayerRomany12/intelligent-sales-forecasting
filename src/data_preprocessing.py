import pandas as pd
import numpy as np
import os

def load_and_merge_datasets(raw_data_dir):
    """Loads and merges the orders, items, products, and translation datasets."""
    print("Loading datasets...")
    orders = pd.read_csv(os.path.join(raw_data_dir, 'olist_orders_dataset.csv'))
    items = pd.read_csv(os.path.join(raw_data_dir, 'olist_order_items_dataset.csv'))
    products = pd.read_csv(os.path.join(raw_data_dir, 'olist_products_dataset.csv'))
    translation = pd.read_csv(os.path.join(raw_data_dir, 'product_category_name_translation.csv'))
    
    print("Merging datasets...")
    # Merge items and products
    items_products = items.merge(products, on='product_id', how='left')
    
    # Add english translation for product category
    items_products = items_products.merge(translation, on='product_category_name', how='left')
    
    # Merge with orders
    merged_df = items_products.merge(orders, on='order_id', how='left')
    return merged_df

def clean_data(df):
    """Cleans the merged dataframe."""
    print("Cleaning data...")
    # Drop canceled or unavailable orders
    df = df[~df['order_status'].isin(['canceled', 'unavailable'])]
    
    # Convert timestamp
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Fill missing product categories with 'unknown'
    df['product_category_name_english'] = df['product_category_name_english'].fillna('unknown')
    
    return df

def aggregate_time_series(df, freq='D'):
    """Aggregates the dataframe into a time series format."""
    print(f"Aggregating time series (freq={freq})...")
    # Set index to timestamp
    df = df.set_index('order_purchase_timestamp')
    
    # Resample and aggregate
    time_series = df.resample(freq).agg(
        total_sales=('price', 'sum'),
        total_items=('order_item_id', 'count'),
        total_orders=('order_id', 'nunique')
    ).fillna(0)
    
    return time_series

if __name__ == "__main__":
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    
    # Execute pipeline
    merged_df = load_and_merge_datasets(raw_dir)
    cleaned_df = clean_data(merged_df)
    ts_df = aggregate_time_series(cleaned_df, freq='D')
    
    # Save output
    output_path = os.path.join(processed_dir, 'time_series_sales.csv')
    ts_df.to_csv(output_path)
    print(f"Processed time series data saved to {output_path}")
