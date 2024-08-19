import os
import warnings

import numpy as np
import joblib
import pandas as pd
import psycopg2
from sklearn.metrics import mean_squared_error
from column_generator import get_column_names, build_training_features
from config import db_connect, TABLE_NAME

# Determine if running in AWS Lambda or locally
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None
current_script_dir = os.path.dirname(__file__)
EFS_MOUNT_POINT = '/mnt/efs' if IS_LAMBDA else os.path.join(current_script_dir, '..')
input_file_path = os.path.join(EFS_MOUNT_POINT, 'data', 'current_state.pkl')


def load_data():
    return pd.read_pickle(input_file_path)


def filter_rows_with_null_forecasts(data):
    forecast_columns = [
        'bags_used_forecast',
        'cold_bags_used_forecast',
        'deep_frozen_bags_used_forecast',
    ]
    return data[data[forecast_columns].isna().any(axis=1)]


def load_model(target_column, hub_id):
    model_path = os.path.join(
        EFS_MOUNT_POINT, 'models', f"{target_column}_{hub_id}.joblib"
    )
    return joblib.load(model_path)


def make_predictions(data, hub_id, features):
    target_columns = ['cold_bags', 'bags', 'deep_frozen_bags']

    for target_column in target_columns:
        model = load_model(target_column, hub_id)
        # target_column_name = f"{target_column}_used"
        forecast_column_name = f"{target_column}_used_forecast"
        hub_data = data[data.hub_id == hub_id]
        # Filter the data for the specific hub_id
        hub_data = data[data.hub_id == hub_id]
        
        # Safely assign the predicted values back to the original DataFrame using .loc[]
        data.loc[data.hub_id == hub_id, forecast_column_name] = model.predict(hub_data[features].values)
    return data


def update_postgresql(data):
    conn = db_connect()
    cur = conn.cursor()
    columns = get_column_names()
    for index, row in data.iterrows():
        update_query = f"""
            UPDATE {TABLE_NAME}
            SET bags_used_forecast = %s,
                cold_bags_used_forecast = %s,
                deep_frozen_bags_used_forecast = %s
            WHERE order_id = %s;
        """
        cur.execute(
            update_query,
            (
                row['bags_used_forecast'],
                row['cold_bags_used_forecast'],
                row['deep_frozen_bags_used_forecast'],
                row['order_id'],
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


def do_predict():
    # Download data from PostgreSQL if necessary
    # download_to_csv()

    # Load data
    data = load_data()

    # Filter rows with null forecasts
    data_with_nulls = filter_rows_with_null_forecasts(data)

    print(f"Prepared {data_with_nulls.shape[0]} rows for prediction")
    # Build features
    features = build_training_features(data_with_nulls.columns)

    # Make predictions
    hub_ids = data_with_nulls['hub_id'].unique()
    for hub_id in hub_ids:
        data_with_nulls = make_predictions(data_with_nulls, hub_id, features)

    # Update PostgreSQL
    update_postgresql(data_with_nulls)

    return "Predictions made and database updated successfully."


def lambda_handler(event, context):
    result = do_predict()
    return {'statusCode': 200, 'body': result}


if __name__ == '__main__':
    print(do_predict())
