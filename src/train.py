import os

import numpy as np
import joblib

import warnings

warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="mlflow.utils.requirements_utils"
)


import mlflow
import pandas as pd
import xgboost as xgb
from joblib import dump
from sklearn.metrics import mean_squared_error
from column_generator import build_training_features
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Determine if running in AWS Lambda or locally
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None

current_script_dir = os.path.dirname(__file__)

# EFS mount point for Lambda
EFS_MOUNT_POINT = '/mnt/efs' if IS_LAMBDA else os.path.join(current_script_dir, '..')
DEVICE = "cpu"

# mlflow.set_tracking_uri("sqlite:///" + os.path.join(EFS_MOUNT_POINT, 'mlflow.db'))
# mlflow.set_tracking_uri("sqlite:///" + os.path.join(EFS_MOUNT_POINT, 'mlflow.db')

input_file_path = os.path.join(EFS_MOUNT_POINT, 'data', 'current_state.pkl')


def train_model(df_filtered, target_column, hub_id, features):

    target_column_name = target_column + '_used'
    forecast_column_name = target_column_name + '_forecast'

    columns = features + [target_column_name] + [forecast_column_name]
    data = df_filtered[df_filtered.hub_id == hub_id][columns]
    data.dropna(inplace=True)
    target = [target_column_name]

    # train = data.sample(frac=0.95)
    # test = data.loc[~data.index.isin(train.index)]

    train, test = train_test_split(data, test_size=0.3, random_state=42)

    if target_column == "deep_frozen_bags":
        params = {
            'bootstrap': False,
            'ccp_alpha': 0.0,
            'criterion': 'squared_error',
            'max_depth': 30,
            'max_features': 'sqrt',
            'max_leaf_nodes': None,
            'max_samples': None,
            'min_impurity_decrease': 0.0,
            'min_samples_leaf': 2,
            'min_samples_split': 10,
            'min_weight_fraction_leaf': 0.0,
            'n_estimators': 800,
            'n_jobs': 6,
            'oob_score': False,
            'random_state': 42,
            'verbose': 0,
            'warm_start': False,
        }

        model = RandomForestRegressor(**params)

    elif target_column == "bags":
        params = {
            'colsample_bytree': 0.8049310664813739,
            'gamma': 0.31904734990860323,
            'learning_rate': 0.020987723995735754,
            'max_depth': 8,
            'n_estimators': 1400,
            'objective': 'reg:squarederror',
            'random_state': 42,
            'subsample': 0.6878477231583816,
            'verbosity': 1,
        }

        model = xgb.XGBRegressor(
            **params,
            device=DEVICE,
        )
        # model = mlflow.pyfunc.load_model('/home/sir/farmy/ch.farmy.scinode/development/9631-update/mlruns/8/dfeb8badb69c493d91fab39c78c9999e/artifacts/model')
    else:
        params = {
            'colsample_bytree': 0.9332506592696221,
            'gamma': 0.33126595740822656,
            'learning_rate': 0.011121117890656158,
            'max_depth': 8,
            'n_estimators': 700,
            'objective': 'reg:squarederror',
            'random_state': 42,
            'subsample': 0.5581688088227714,
            'verbosity': 1,
        }
        model = xgb.XGBRegressor(**params, device=DEVICE)

    model.fit(train[features].values, train[target].values.ravel())

    print("Mean Squared Error between {} and:".format(target_column))
    y_forecast = data[forecast_column_name].values.flatten()
    mse_forecast = mean_squared_error(data[target].values.flatten(), y_forecast)
    print("forecast from DB:           {:.5f} (should be worst)".format(mse_forecast))

    y_test = model.predict(test[features].values).flatten()
    mse_test = mean_squared_error(test[target].values.flatten(), np.around(y_test))
    print(
        "prediction for test slice:  {:.5f} ({:.2f}% improvement)".format(
            mse_test, (mse_forecast - mse_test) / mse_test * 100
        )
    )

    y_train = model.predict(train[features].values).flatten()
    mse_train = mean_squared_error(train[target].values.flatten(), np.around(y_train))
    print(
        "prediction for train slice: {:.5f} (should be smallest but not differ a lot from test MSE)".format(
            mse_train
        )
    )

    # dump(model, 'new/{}_model_v3_hub_{}.joblib'.format(target_column, hub_id), compress=True)
    return model


def dump_pickle(obj, filename: str):
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)


def do_train():
    # Load data from CSV
    data = pd.read_pickle(input_file_path)

    # Filter the DataFrame to skip rows where any of the specified columns have NA values
    df_filtered = data.dropna(
        subset=['bags_used', 'cold_bags_used', 'deep_frozen_bags_used']
    )
    features = build_training_features(df_filtered.columns)

    # print('{}-{} for {}'.format(start_date, end_date, extra_features))
    target_columns = ['cold_bags', 'bags', 'deep_frozen_bags']
    result = []
    for hub_id in [1, 4]:
        print("hub ", hub_id)
        for target_column in target_columns:
            model = train_model(df_filtered, target_column, hub_id, features)
            output_file_path = os.path.join(
                EFS_MOUNT_POINT, 'models', f"{target_column}_{hub_id}.joblib"
            )
            joblib.dump(model, output_file_path, compress=True)
            result.append(
                f"Model for prediction of {target_column} of hub {hub_id} trained and saved to {output_file_path}"
            )

    return result


def lambda_handler(event, context):
    result = do_train()
    return {'statusCode': 200, 'body': result}


if __name__ == '__main__':
    print(do_train())
