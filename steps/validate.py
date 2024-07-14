import os
import json

import numpy as np
import pandas as pd
from evidently import ColumnMapping
from evidently.tests import *
from evidently.report import Report
from evidently.metrics import *
from evidently.test_suite import TestSuite
from evidently.test_preset import (
    DataStabilityTestPreset,
    NoTargetPerformanceTestPreset
)
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
from evidently.tests.base_test import generate_column_tests
from evidently.metrics.base_metric import generate_column_metrics

# Determine if running in AWS Lambda or locally
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None

# EFS mount point for Lambda
current_script_dir = os.path.dirname(__file__)
EFS_MOUNT_POINT = '/mnt/efs' if IS_LAMBDA else os.path.join(current_script_dir, '../data')

input_file_path = os.path.join(EFS_MOUNT_POINT, 'current_state.pkl')
output_file_path = os.path.join(EFS_MOUNT_POINT, 'data_drift.json')



def run(df_enriched):
    timezone = df_enriched['delivery_time'].iloc[0].tzinfo
    start_date = pd.to_datetime('2022-01-01').tz_localize(timezone)
    end_date = pd.to_datetime('2022-02-20').tz_localize(timezone)

    report = Report(metrics=[DataDriftPreset()])

    reference = df_enriched[
        (df_enriched['delivery_time'] > start_date)
        & (df_enriched['delivery_time'] < end_date)
    ]
    current = df_enriched[(df_enriched['delivery_time'] >= end_date)]

    # Verify non-empty datasets for the report
    if reference.empty:
        raise ValueError("The reference dataset is empty. Please check the date range.")
    if current.empty:
        raise ValueError("The current dataset is empty. Please check the date range.")

    # Ensure no missing values and correct data types for correlation calculation
    num_columns = reference.select_dtypes(include=[np.number]).columns.tolist()
    reference = reference[num_columns].dropna()
    print(current.head())
    current = current[num_columns].dropna()
    print(current.head())
#    print(reference.head())
    if reference.empty or current.empty:
        raise ValueError(
            "The datasets must contain numeric columns without missing values for correlation calculation."
        )

    # Run the report
    report.run(reference_data=reference, current_data=current)

    return report.as_dict()



def remove_forecast_columns(data: pd.DataFrame) -> pd.DataFrame:
    # Identify columns ending with '_forecast'
    forecast_columns = data.filter(regex='_forecast$').columns
    
    # Drop these columns from the DataFrame
    data = data.drop(columns=forecast_columns)
    
    return data


def main():
    data = pd.read_pickle(input_file_path)
    data = remove_forecast_columns(data)
    result = run(data)
    with open(output_file_path, 'w') as fp:
        json.dump(result, fp, indent=4, default=str)
    return result


def lambda_handler(event, context):
    result = main()
    json = json.dumps(result, indent=4, default=str)
    return {'statusCode': 200, 'body': json}


if __name__ == '__main__':
    print(main())
