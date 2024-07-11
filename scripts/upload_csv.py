# upload_csv.py
import psycopg2
import pandas as pd
import os
from column_generator import generate_columns, get_column_names

DEFAULT_DBNAME = 'data_warehouse'
DEFAULT_USERNAME = 'postgres'
DEFAULT_PASSWORD = 'postgres'
DEFAULT_ENDPOINT = 'localhost:5432'
TABLE_NAME = 'bags_forecast'

# Get parameters from environment variables
db_endpoint = os.getenv('DB_ENDPOINT', DEFAULT_ENDPOINT)
db_username = os.getenv('DB_USERNAME', DEFAULT_USERNAME)
db_password = os.getenv('DB_PASSWORD', DEFAULT_PASSWORD)
db_name = os.getenv('DB_NAME', DEFAULT_DBNAME)

# Example path to the CSV file
csv_file_path = '../dataset/bags_forecast_with_id.csv'

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host=db_endpoint.split(':')[0],
    port=db_endpoint.split(':')[1],
    database=db_name,
    user=db_username,
    password=db_password
)

# Create a cursor
cur = conn.cursor()

cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
# Generate the table structure dynamically
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    {', '.join(generate_columns())}
);
"""
cur.execute(create_table_query)
conn.commit()

# Load data from CSV
data = pd.read_csv(csv_file_path)

# Insert data into the table
columns = get_column_names()
insert_query = f"""
INSERT INTO {TABLE_NAME} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))});
"""

#for _, row in data.iterrows():
#    cur.execute(insert_query, tuple(row))

conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

