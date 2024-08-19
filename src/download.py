import os

import pandas as pd
import psycopg2
from column_generator import get_column_names
from config import db_connect

TABLE_NAME = 'bags_forecast'

# Determine if running in AWS Lambda or locally
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None

# EFS mount point for Lambda
current_script_dir = os.path.dirname(__file__)
EFS_MOUNT_POINT = (
    '/mnt/efs' if IS_LAMBDA else os.path.join(current_script_dir, '../data')
)

# Path to the output CSV file
DEFAULT_CSV_OUTPUT = os.path.join(EFS_MOUNT_POINT, 'current_state.csv')


def select_to_df():
    conn = db_connect()
    cur = conn.cursor()
    columns = get_column_names()

    # Query to select all data from the table
    select_query = f"SELECT {', '.join(columns)} FROM {TABLE_NAME};"
    cur.execute(select_query)

    # Fetch all rows from the table
    rows = cur.fetchall()

    # Create a DataFrame from the fetched data
    data = pd.DataFrame(rows, columns=columns)
    # Close the cursor and connection
    cur.close()
    conn.close()

    return data


def download_to_csv(output_csv_file_path=DEFAULT_CSV_OUTPUT):
    data = select_to_df()
    # Save the DataFrame to a CSV file
    data.to_csv(output_csv_file_path, index=False)

    return f"Data successfully downloaded to {output_csv_file_path}"


def lambda_handler(event, context):
    result = download_to_csv()
    return {'statusCode': 200, 'body': result}


if __name__ == '__main__':
    print(download_to_csv())
