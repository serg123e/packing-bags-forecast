import os

import pandas as pd
import psycopg2
from column_generator import get_column_names

DEFAULT_DBNAME = 'data_warehouse'
DEFAULT_USERNAME = 'postgres'
DEFAULT_PASSWORD = 'postgres'
DEFAULT_ENDPOINT = 'localhost:5432'
TABLE_NAME = 'bags_forecast'

# Determine if running in AWS Lambda or locally
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None

# EFS mount point for Lambda
current_script_dir = os.path.dirname(__file__)
EFS_MOUNT_POINT = (
    '/mnt/efs' if IS_LAMBDA else os.path.join(current_script_dir, '../data')
)


def download_to_csv():
    # Get parameters from environment variables
    db_endpoint = os.getenv('DB_ENDPOINT', DEFAULT_ENDPOINT)
    db_username = os.getenv('DB_USERNAME', DEFAULT_USERNAME)
    db_password = os.getenv('DB_PASSWORD', DEFAULT_PASSWORD)
    db_name = os.getenv('DB_NAME', DEFAULT_DBNAME)

    # Path to the output CSV file
    output_csv_file_path = os.path.join(EFS_MOUNT_POINT, 'current_state.csv')

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=db_endpoint.split(':')[0],
        port=db_endpoint.split(':')[1],
        database=db_name,
        user=db_username,
        password=db_password,
    )

    # Create a cursor
    cur = conn.cursor()

    # Get column names in the correct order
    columns = get_column_names()

    # Query to select all data from the table
    select_query = f"SELECT {', '.join(columns)} FROM {TABLE_NAME};"
    cur.execute(select_query)

    # Fetch all rows from the table
    rows = cur.fetchall()

    # Create a DataFrame from the fetched data
    data = pd.DataFrame(rows, columns=columns)

    # Save the DataFrame to a CSV file
    data.to_csv(output_csv_file_path, index=False)

    # Close the cursor and connection
    cur.close()
    conn.close()

    return f"Data successfully downloaded to {output_csv_file_path}"


def lambda_handler(event, context):
    result = download_to_csv()
    return {'statusCode': 200, 'body': result}


if __name__ == '__main__':
    print(download_to_csv())
