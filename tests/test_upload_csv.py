import os
import sys

import pytest
import pandas as pd

## Add the parent directory to the Python path
scripts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')
steps_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'steps')
sys.path.append(scripts_path)
sys.path.append(steps_path)

from config import db_connect, TABLE_NAME


from column_generator import generate_columns, get_column_names
from upload_csv import do_upload
from download import download_to_csv
from ingest import do_ingest
from transform import do_transform
# from train import do_train



def test_upload():
    csv_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'bags_forecast_with_id.csv')

    conn = db_connect()
    cur = conn.cursor()

    do_upload(csv_file_path, 0.01)

    # Query to select all data from the table
    select_query = f"SELECT count(*) FROM {TABLE_NAME} LIMIT 1"
    cur.execute(select_query)

    # Fetch all rows from the table
    rows = cur.fetchall()

    assert rows[0][0] >= 1000

    # Close the cursor and connection
    cur.close()
    conn.close()

