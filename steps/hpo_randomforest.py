import os
import json

import numpy as np
import mlflow
import pandas as pd
from joblib import dump
from hyperopt import STATUS_OK, Trials, hp, tpe, fmin
from hyperopt.pyll import scope
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from column_generator import build_training_features

# Determine if running in AWS Lambda or locally
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None

current_script_dir = os.path.dirname(__file__)

# EFS mount point for Lambda
EFS_MOUNT_POINT = '/mnt/efs' if IS_LAMBDA else os.path.join(current_script_dir, '../data')

# mlflow.set_tracking_uri("sqlite:///" + os.path.join(EFS_MOUNT_POINT, 'mlflow.db'))
# mlflow.set_tracking_uri("sqlite:///" + os.path.join(EFS_MOUNT_POINT, 'mlflow.db')

input_file_path = os.path.join(EFS_MOUNT_POINT, 'current_state.pkl')
output_file_path = os.path.join(EFS_MOUNT_POINT, 'hpo_randomforest.json')
max_evals = os.getenv("HPO_MAX_EVALS", 10)

mlflow.set_experiment("hpo-bags")


def build_names(target_column):
    target_column_name = target_column + '_used'
    forecast_column_name = target_column + '_used_forecast'

    return target_column_name, forecast_column_name


def data_for_target(df, target_column, hub_id):
    features = build_training_features(df)

    target_column_name, forecast_column_name = build_names(target_column)

    necessary_columns = features + [target_column_name] + [forecast_column_name]
    data = df[df.hub_id == hub_id][necessary_columns]
    data.dropna(inplace=True)
    return data


def hpo(df, target, hub_id):
    def objective(params):
        with mlflow.start_run():
            print(params)
            mlflow.log_params(params)
            mlflow.log_param('features', str(features))
            mlflow.set_tag('regressor', 'randomforest')
            mlflow.set_tag('target', target)
            mlflow.log_param('hub_id', hub_id)

            X_train = train[features].values
            y_train = train[target].values
            X_val = test[features].values
            y_val = test[target].values

            model = RandomForestRegressor(**params)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_val)
            rmse = mean_squared_error(y_val, y_pred, squared=False)
            mlflow.log_metric("rmse", rmse)

        return {'loss': rmse, 'status': STATUS_OK}

    features = build_training_features(df)
    train, test = train_test_split(df, test_size=0.3, random_state=42)

    space = {
        'bootstrap': hp.choice('bootstrap', [False]),
        'ccp_alpha': hp.uniform('ccp_alpha', 0.0, 0.1),
        'criterion': hp.choice('criterion', ['squared_error']),
        'max_depth': scope.int(hp.quniform('max_depth', 20, 40, 1)),
        'max_features': hp.choice('max_features', ['sqrt']),
        'max_leaf_nodes': hp.choice('max_leaf_nodes', [None]),
        'max_samples': hp.choice('max_samples', [None]),
        'min_impurity_decrease': hp.uniform('min_impurity_decrease', 0.0, 0.1),
        'min_samples_leaf': scope.int(hp.quniform('min_samples_leaf', 1, 5, 1)),
        'min_samples_split': scope.int(hp.quniform('min_samples_split', 5, 15, 1)),
        'min_weight_fraction_leaf': hp.uniform('min_weight_fraction_leaf', 0.0, 0.1),
        'n_estimators': scope.int(hp.quniform('n_estimators', 700, 900, 100)),
        'n_jobs': hp.choice('n_jobs', [6]),
        'oob_score': hp.choice('oob_score', [False]),
        'random_state': hp.choice('random_state', [42]),
        'verbose': hp.choice('verbose', [0]),
        'warm_start': hp.choice('warm_start', [False])
    }

    trials = Trials()
    best = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=max_evals, trials=trials)

    return best

def run(data):
    target_columns = ['deep_frozen_bags' , 'cold_bags', 'bags']

    result = {}
    for hub_id in [1, 4]:
        print("hub ", hub_id)
        for target_column_prefix in target_columns:
            df = data_for_target(data, target_column_prefix, hub_id)
            target_column_name, _ = build_names(target_column_prefix)
            target = target_column_name

            best_params = hpo(df, target)
            if target_column_prefix not in result:
                result[target_column_prefix] = {}
            result[target_column_prefix][hub_id] = best_params

            # model = train_model(df, best_params, target, features)
            # save_model(model, target_column, hub_id)
    print(result)
    return result


def main():
    data = pd.read_pickle(input_file_path)
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
