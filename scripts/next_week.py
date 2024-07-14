import pandas as pd
import psycopg2
import json
from datetime import datetime, timedelta, date
from decimal import Decimal, getcontext, ROUND_HALF_UP
import os
from tqdm import tqdm

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
    data['delivery_time'] = pd.to_datetime(data['delivery_time'], utc=True)
    return data

# Convert numerical columns to Decimal and datetime columns to string
def convert_to_compatible_types(data):
    return data

# Filter data for PostgreSQL load
def filter_data(data, current_date):
    current_date = pd.to_datetime(current_date, utc=True)

    start_of_current_week = current_date - timedelta(days=current_date.weekday())
    start_of_next_week = start_of_current_week + timedelta(weeks=1)
    start_of_previous_week = start_of_current_week - timedelta(weeks=1)

    previous_week_data = data[(data['delivery_time'] >= start_of_previous_week) & (data['delivery_time'] < start_of_current_week)]
    current_week_data = data[(data['delivery_time'] >= start_of_current_week) & (data['delivery_time'] < start_of_next_week)]
    next_week_data = data[(data['delivery_time'] >= start_of_next_week) & (data['delivery_time'] < start_of_next_week + timedelta(weeks=1))]

    next_week_data = next_week_data.drop(columns=[col for col in next_week_data.columns if '_used' in col])
    next_week_data = next_week_data.drop(columns=[col for col in next_week_data.columns if '_forecast' in col])

    return previous_week_data, current_week_data, next_week_data

# Filter all previous weeks data
def filter_all_previous_weeks(data, current_date):
    current_date = pd.to_datetime(current_date, utc=True)

    start_of_current_week = current_date - timedelta(days=current_date.weekday())
    previous_weeks_data = data[data['delivery_time'] < start_of_current_week]

    return previous_weeks_data

# Check if PostgreSQL table is empty
def is_postgres_empty(table_name, conn):
    cur = conn.cursor()
    cur.execute(f"SELECT EXISTS (SELECT 1 FROM {TABLE_NAME} LIMIT 1);")
    result = cur.fetchone()[0]
    cur.close()
    return not result

# Load data into PostgreSQL
def load_to_postgres(label, data, table_name, conn):
    data = convert_to_compatible_types(data)

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
    for row in tqdm(data.itertuples(index=False), total=len(data), desc=f"Loading {label} data to PostgreSQL DB"):
        row = tuple(None if pd.isna(x) else x for x in row)
        cur.execute(insert_query, row)
    conn.commit()
    cur.close()

# Update configuration date
def update_config_date(config):
    current_date = pd.to_datetime(config['current_date'], utc=True)
    new_date = current_date + timedelta(weeks=1)
    config['current_date'] = new_date.isoformat()

# Main function
def main():
    current_script_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_script_dir, '../data/bags_forecast_with_id.csv')
    config_path = os.path.join(current_script_dir, './next_week.json')
    
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
        # Load all previous weeks data until the "current week"
        previous_weeks_data = filter_all_previous_weeks(data, current_date)
        load_to_postgres("all previous", previous_weeks_data, table_name, conn)
    else:
        # Filter data for previous, current, and next week
        previous_week_data, current_week_data, next_week_data = filter_data(data, current_date)
        load_to_postgres("previous week", previous_week_data, table_name, conn)
        load_to_postgres(f"current week {current_date}", current_week_data, table_name, conn)
        load_to_postgres("next week filtered", next_week_data, table_name, conn)

    # Update configuration date
    update_config_date(config)
    save_config(config, config_path)

    # Close PostgreSQL connection
    conn.close()

if __name__ == '__main__':
    main()
