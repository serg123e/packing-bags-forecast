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


def extra_features(data: DataFrame, *args, **kwargs) -> DataFrame:
    df_enriched = data.copy()
    df_enriched['day_of_year'] = df_enriched['delivery_time'].dt.dayofyear
    df_enriched['day_of_week'] = df_enriched['delivery_time'].dt.dayofweek
    df_enriched['number_of_week'] = df_enriched['delivery_time'].dt.isocalendar().week
    df_enriched['delivery_hour'] = df_enriched['delivery_time'].dt.hour
    return df_enriched


def remove_outliers(df: DataFrame, *args, **kwargs) -> DataFrame:
    df = df[df.bags_used < 10]
    df = df[df.bags_used > 0]
    df = df[df.cold_bags_used > 0]
    df = df[df.deep_frozen_bags_used > 0]
    df = df[df.total_weight < 5e4]
    df.fillna(0.0, inplace=True)
    return df


def main():
    # Load data from CSV
    data = pd.read_pickle(input_file_path)

    # Apply transformations
    data = transform(data)
    data = extra_features(data)
    data = remove_outliers(data)

    # Save the DataFrame as a pickle file
    data.to_pickle(output_file_path)

    print(f"Data successfully transformed and saved to {output_file_path}")


def lambda_handler(event, context):
    main()
    return {
        'statusCode': 200,
        'body': f"Data successfully transformed and saved to {output_file_path}",
    }


if __name__ == '__main__':
    main()
