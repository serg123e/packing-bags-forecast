import os
import psycopg2

TABLE_NAME = 'bags_forecast'


def db_connect():
    DEFAULT_DBNAME = 'data_warehouse'
    DEFAULT_USERNAME = 'postgres'
    DEFAULT_PASSWORD = 'postgres'
    DEFAULT_ENDPOINT = 'localhost:5432'

    # Get parameters from environment variables
    db_endpoint = os.getenv('DB_ENDPOINT', DEFAULT_ENDPOINT)
    db_username = os.getenv('DB_USERNAME', DEFAULT_USERNAME)
    db_password = os.getenv('DB_PASSWORD', DEFAULT_PASSWORD)
    db_name = os.getenv('DB_NAME', DEFAULT_DBNAME)

    # Example path to the CSV file

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=db_endpoint.split(':')[0],
        port=db_endpoint.split(':')[1],
        database=db_name,
        user=db_username,
        password=db_password,
    )

    return conn
