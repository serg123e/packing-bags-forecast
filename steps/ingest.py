import os
import pandas as pd
from pandas import DataFrame

# Determine if running in AWS Lambda or locally
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None

# EFS mount point for Lambda
EFS_MOUNT_POINT = '/mnt/efs' if IS_LAMBDA else '.'

# Path to the input CSV file
input_csv_file_path = os.path.join(EFS_MOUNT_POINT, 'current_state.csv')
# Path to the output pickle file
output_pickle_file_path = os.path.join(EFS_MOUNT_POINT, 'current_state.pkl')

def transform(data: DataFrame, *args, **kwargs) -> DataFrame:
    data['delivery_time'] = pd.to_datetime(data['delivery_time'], utc=True)
    return data

def main():
    # Load data from CSV
    data = pd.read_csv(input_csv_file_path)

    # Apply transformations
    data = transform(data)

    # Save the DataFrame as a pickle file
    data.to_pickle(output_pickle_file_path)

    print(f"Data successfully ingested and saved to {output_pickle_file_path}")

def lambda_handler(event, context):
    main()
    return {
        'statusCode': 200,
        'body': f"Data successfully ingested and saved to {output_pickle_file_path}"
    }

if __name__ == '__main__':
    main()