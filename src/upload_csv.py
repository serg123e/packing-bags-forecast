# upload_csv.py
import os
import warnings
import pandas as pd
from column_generator import generate_columns, get_column_names
from config import db_connect, TABLE_NAME


def do_upload(csv_file_path, fraction=1.0):
    # Suppress deprecation warning
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="pandas.core.dtypes.cast"
    )

    conn = db_connect()

    # Create a cursor
    cur = conn.cursor()

    cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
    # Generate the table structure dynamically
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {', '.join(generate_columns())}
    );
    """
    print(create_table_query)
    cur.execute(create_table_query)
    conn.commit()

    # Load data from CSV
    data = pd.read_csv(csv_file_path)
    # Convert NaN to None (interpreted as NULL in PostgreSQL)
    # data = data.where(pd.notnull(data), None)
    data = data.replace({float('nan'): None})
    data = data.sample(frac=fraction, random_state=42)

    # Insert data into the table
    columns = get_column_names()
    insert_query = f"""
    INSERT INTO {TABLE_NAME} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))});
    """

    for _, row in data.iterrows():
        cur.execute(insert_query, tuple(row))

    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()


if __name__ == '__main__':
    csv_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        'data',
        'bags_forecast_with_id.csv',
    )
    do_upload(csv_file_path)
