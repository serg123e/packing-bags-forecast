import os
import sys
import pytest

import pandas as pd
import psycopg2


## Add the parent directory to the Python path
scripts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')
steps_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'steps')
sys.path.append(scripts_path)
sys.path.append(steps_path)

from column_generator import generate_columns, get_column_names
from upload_csv import do_upload
from download import download_to_csv
from ingest import do_ingest
from transform import do_transform
from train import do_train
from predict import do_predict
from config import db_connect


def clean_last_forecasts(count):
    conn = db_connect()
    try:
        with conn.cursor() as cur:
            # Order table by order_id and update the last {count} rows
            cur.execute("""
                UPDATE bags_forecast
                SET bags_used_forecast = NULL,
                    cold_bags_used_forecast = NULL,
                    deep_frozen_bags_used_forecast = NULL
                WHERE order_id IN (
                    SELECT order_id
                    FROM bags_forecast
                    ORDER BY order_id DESC
                    LIMIT %s
                )
            """, (count,))
            conn.commit()
    finally:
        conn.close()

def need_to_predict_rows_count():
    conn = db_connect()
    try:
        with conn.cursor() as cur:
            # Count rows where forecast columns are NULL
            cur.execute("""
                SELECT COUNT(*)
                FROM bags_forecast
                WHERE bags_used_forecast IS NULL
                AND cold_bags_used_forecast IS NULL
                AND deep_frozen_bags_used_forecast IS NULL
            """)
            count = cur.fetchone()[0]
            return count
    finally:
        conn.close()

def test_integration():
    test_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests', 'test.csv')
    do_upload(test_csv)
    download_to_csv()

    do_ingest()
    do_transform()
    do_train()
    return None


    assert( need_to_predict_rows_count() == 1 )
    clean_last_forecasts(100)
    assert( need_to_predict_rows_count() == 100 )

    download_to_csv()
    do_ingest()
    do_predict()

    assert( need_to_predict_rows_count() == 0 )


if __name__ == '__main__':
    pytest.main()
