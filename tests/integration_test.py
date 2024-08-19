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
from ingest import ingest_csv
from transform import do_transform
from train import do_train
from predict import do_predict

def test_integration():

    test_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests', 'test.csv')
    do_upload(test_csv)
    download_to_csv()
    ingest_csv()
    do_transform()
    #do_train()
    #do_predict()


if __name__ == '__main__':
    pytest.main()
