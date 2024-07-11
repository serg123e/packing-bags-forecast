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
#    data['order_id'] = data['order_id'].astype(str)

#    for col in data.select_dtypes(include=['float64']).columns:
#        data[col] = data[col].apply(lambda x: str(round(x, 6)) if pd.notnull(x) else '0')
#    for col in data.select_dtypes(include=['datetime64[ns, UTC]']).columns:
#        data[col] = data[col].astype(str)
    return data

# Filter data for PostgreSQL load
def filter_data(data, current_date, yesterday_date=pd.to_datetime(date(2000, 1, 1), utc=True)):
    data['delivery_time'] = pd.to_datetime(data['delivery_time'], utc=True)
    current_date = pd.to_datetime(current_date, utc=True)

    today_data = data[(data['delivery_time'] >= yesterday_date) & (data['delivery_time'] < current_date)]
    tomorrow_data = data[(data['delivery_time'] >= current_date) & (data['delivery_time'] < current_date + timedelta(days=1))]

    tomorrow_data = tomorrow_data.drop(columns=[col for col in tomorrow_data.columns if '_used' in col])

    return today_data, tomorrow_data

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
    # data = data.where(pd.notnull(data), None)

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
    new_date = current_date + timedelta(days=1)
    config['current_date'] = new_date.isoformat()

# Main function
def main():
    config_path = 'next_day.json'
    csv_path = '../dataset/bags_forecast_with_id.csv'
    
    table_name = TABLE_NAME
    # Load configuration
    config = load_config(config_path)

    # Load data
    data = load_data(csv_path)
    # data.fillna(0.0, inplace=True)

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
        # Load all data until the "current date"
        today_data, _ = filter_data(data, current_date)
        load_to_postgres(today_data, table_name, conn)
    else:
        # Filter data for "today" and "tomorrow"
        yesterday_date = current_date - timedelta(days=1)
        today_data, tomorrow_data = filter_data(data, current_date, yesterday_date)
        load_to_postgres(today_data, table_name, conn)
        load_to_postgres(tomorrow_data, table_name, conn)

    # Update configuration date
    update_config_date(config)
    save_config(config, config_path)

    # Close PostgreSQL connection
    conn.close()

if __name__ == '__main__':
    main()
