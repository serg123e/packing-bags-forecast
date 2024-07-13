import pandas as pd
import psycopg2
import json
from datetime import datetime, timedelta, date
from decimal import Decimal, getcontext, ROUND_HALF_UP
import os

DEFAULT_DBNAME = 'data_warehouse'
DEFAULT_USERNAME = 'postgres'
DEFAULT_PASSWORD = 'postgres'
DEFAULT_ENDPOINT = 'localhost:5432'

TABLE_NAME = 'bags_forecast'

# Configure decimal context for precise rounding
getcontext().prec = 10
getcontext().rounding = ROUND_HALF_UP

# Load configuration file
def load_config(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config

# Save configuration file
def save_config(config, config_path):
    with open(config_path, 'w') as file:
        json.dump(config, file)

# Load data from CSV file
def load_data(csv_path):
    data = pd.read_csv(csv_path)
    return data

# Convert numerical columns to Decimal and datetime columns to string
def convert_to_compatible_types(data):
    return data

# Filter data for PostgreSQL load
def filter_data(data, current_date):
    data['delivery_time'] = pd.to_datetime(data['delivery_time'], utc=True)
    current_date = pd.to_datetime(current_date, utc=True)

    start_of_current_month = current_date.replace(day=1)
    start_of_next_month = (start_of_current_month + pd.DateOffset(months=1)).replace(day=1)
    start_of_previous_month = (start_of_current_month - pd.DateOffset(months=1)).replace(day=1)

    previous_month_data = data[(data['delivery_time'] >= start_of_previous_month) & (data['delivery_time'] < start_of_current_month)]
    current_month_data = data[(data['delivery_time'] >= start_of_current_month) & (data['delivery_time'] < start_of_next_month)]
    next_month_data = data[(data['delivery_time'] >= start_of_next_month) & (data['delivery_time'] < start_of_next_month + pd.DateOffset(months=1))]

    next_month_data = next_month_data.drop(columns=[col for col in next_month_data.columns if '_used' in col])

    return previous_month_data, current_month_data, next_month_data

# Check if PostgreSQL table is empty
def is_postgres_empty(table_name, conn):
    cur = conn.cursor()
    cur.execute(f"SELECT EXISTS (SELECT 1 FROM {TABLE_NAME} LIMIT 1);")
    result = cur.fetchone()[0]
    cur.close()
    return not result

# Remove duplicates based on 'order_id'
def remove_duplicates(data):
    data = data.drop_duplicates(subset=['order_id'])
    return data

# Load data into PostgreSQL
def load_to_postgres(data, table_name, conn):
    data = convert_to_compatible_types(data)
    data = remove_duplicates(data)

    # Replace NaN with None to handle NULL values in PostgreSQL
    data = data.where(pd.notnull(data), None)

    columns = data.columns.tolist()
    real_bags_used_columns = [
        'bags_used', 'cold_bags_used', 'deep_frozen_bags_used'
    ]
    update_columns = ', '.join([f"{col} = EXCLUDED.{col}" for col in real_bags_used_columns])
    
    insert_query = f"""
    INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})
    ON CONFLICT (order_id) DO UPDATE SET {update_columns};
    """

    cur = conn.cursor()
    for _, row in data.iterrows():
        row = tuple(None if pd.isna(x) else x for x in row)
        print(".", end="")
        cur.execute(insert_query, tuple(row))
    conn.commit()
    cur.close()

# Update configuration date
def update_config_date(config):
    current_date = pd.to_datetime(config['current_date'], utc=True)
    new_date = (current_date + pd.DateOffset(months=1)).replace(day=1)
    config['current_date'] = new_date.isoformat()

# Main function
def main():
    config_path = 'next_month.json'
    csv_path = '../dataset/bags_forecast_with_id.csv'
    
    table_name = TABLE_NAME
    # Load configuration
    config = load_config(config_path)

    # Load data
    data = load_data(csv_path)

    current_date = pd.to_datetime(config['current_date'])

    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        host=os.getenv('DB_ENDPOINT', DEFAULT_ENDPOINT).split(':')[0],
        port=os.getenv('DB_ENDPOINT', DEFAULT_ENDPOINT).split(':')[1],
        database=os.getenv('DB_NAME', DEFAULT_DBNAME),
        user=os.getenv('DB_USERNAME', DEFAULT_USERNAME),
        password=os.getenv('DB_PASSWORD', DEFAULT_PASSWORD)
    )

    # Check if PostgreSQL table is empty
    if is_postgres_empty(table_name, conn):
        # Load all data until the "current month"
        previous_month_data, current_month_data, _ = filter_data(data, current_date)
        load_to_postgres(previous_month_data, table_name, conn)
        load_to_postgres(current_month_data, table_name, conn)
    else:
        # Filter data for previous, current, and next month
        previous_month_data, current_month_data, next_month_data = filter_data(data, current_date)
        load_to_postgres(previous_month_data, table_name, conn)
        load_to_postgres(current_month_data, table_name, conn)
        load_to_postgres(next_month_data, table_name, conn)

    # Update configuration date
    update_config_date(config)
    save_config(config, config_path)

    # Close PostgreSQL connection
    conn.close()

if __name__ == '__main__':
    main()

