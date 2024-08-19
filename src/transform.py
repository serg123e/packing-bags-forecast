import os

import pandas as pd
from pandas import DataFrame

# Determine if running in AWS Lambda or locally
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None

# EFS mount point for Lambda
current_script_dir = os.path.dirname(__file__)
EFS_MOUNT_POINT = (
    '/mnt/efs' if IS_LAMBDA else os.path.join(current_script_dir, '../data')
)

input_file_path = os.path.join(EFS_MOUNT_POINT, 'current_state.pkl')
output_file_path = os.path.join(EFS_MOUNT_POINT, 'current_state.pkl')


def transform(data: DataFrame, *args, **kwargs) -> DataFrame:
    data['delivery_time'] = pd.to_datetime(data['delivery_time'], utc=True)
    return data


def remove_outliers(df: DataFrame, *args, **kwargs) -> DataFrame:
    df = df[df.bags_used < 10]
    df = df[df.bags_used >= 0]
    df = df[df.cold_bags_used >= 0]
    df = df[df.deep_frozen_bags_used >= 0]
    df = df[df.total_weight < 5e4]
    df.fillna(0.0, inplace=True)
    return df


def do_transform():
    # Load data from CSV
    data = pd.read_pickle(input_file_path)

    # Apply transformations
    data = transform(data)
    data = remove_outliers(data)

    # Save the DataFrame as a pickle file
    data.to_pickle(output_file_path)

    print(f"Data successfully transformed and saved to {output_file_path}")


def lambda_handler(event, context):
    do_transform()
    return {
        'statusCode': 200,
        'body': f"Data successfully transformed and saved to {output_file_path}",
    }


if __name__ == '__main__':
    do_transform()
