import os

import pandas as pd
from pandas import DataFrame

# Determine if running in AWS Lambda or locally
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None


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


def do_ingest():
    # EFS mount point for Lambda
    current_script_dir = os.path.dirname(__file__)
    EFS_MOUNT_POINT = (
        '/mnt/efs' if IS_LAMBDA else os.path.join(current_script_dir, '../data')
    )
    # Path to the input CSV file
    input_csv_file_path = os.path.join(EFS_MOUNT_POINT, 'current_state.csv')
    # Path to the output pickle file
    output_pickle_file_path = os.path.join(EFS_MOUNT_POINT, 'current_state.pkl')

    # Load data from CSV
    data = pd.read_csv(input_csv_file_path)

    # Apply transformations
    data = transform(data)
    data = extra_features(data)

    # Print first and last delivery_time found
    first_delivery_time = data['delivery_time'].min()
    last_delivery_time = data['delivery_time'].max()
    print(f"First delivery time: {first_delivery_time}")
    print(f"Last delivery time: {last_delivery_time}")
    # Save the DataFrame as a pickle file
    data.to_pickle(output_pickle_file_path)

    print(f"Data successfully ingested and saved to {output_pickle_file_path}")


def lambda_handler(event, context):
    do_ingest()
    return {
        'statusCode': 200,
        'body': f"Data successfully ingested and saved to {output_pickle_file_path}",
    }


if __name__ == '__main__':
    do_ingest()
