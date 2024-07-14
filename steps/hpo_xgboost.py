import os
import json

import numpy as np
import mlflow
import pandas as pd
import xgboost as xgb
from joblib import dump
from hyperopt import STATUS_OK, Trials, hp, tpe, fmin
from hyperopt.pyll import scope
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# Determine if running in AWS Lambda or locally
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None

# EFS mount point for Lambda
EFS_MOUNT_POINT = '/mnt/efs' if IS_LAMBDA else '.'

mlflow.set_tracking_uri("sqlite:///" + os.path.join(EFS_MOUNT_POINT, 'mlflow.db'))
# mlflow.set_tracking_uri("sqlite:///" + os.path.join(EFS_MOUNT_POINT, 'mlflow.db')

input_file_path = os.path.join(EFS_MOUNT_POINT, 'current_state.pkl')
output_file_path = os.path.join(EFS_MOUNT_POINT, 'hpo_xgboost.json')
max_evals = os.getenv("HPO_MAX_EVALS", 10)


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
            mlflow.set_tag('regressor', 'xgboost')
            mlflow.set_tag('target', target)
            mlflow.log_param('hub_id', hub_id)

            # model = RandomForestRegressor(**params)
            X_train = train[features].values
            y_train = train[target].values
            print(X_train[0])
            print(y_train[0])
            X_val = test[features].values
            y_val = test[target].values
            train_matrix = xgb.DMatrix(X_train, label=y_train)
            valid_matrix = xgb.DMatrix(X_val, label=y_val)
            model = xgb.train(
                params=params,
                # device="cuda", tree_method="gpu_hist",
                dtrain=train_matrix,
                num_boost_round=1000,
                evals=[(valid_matrix, 'validation')],
                early_stopping_rounds=50,
            )
            y_pred = model.predict(valid_matrix)
            rmse = mean_squared_error(y_val, y_pred, squared=False)
            mlflow.log_metric("rmse", rmse)

        return {'loss': rmse, 'status': STATUS_OK}

    features = build_training_features(df)
    train, test = train_test_split(df, test_size=0.3, random_state=42)

    space = {
        # 'booster': hp.choice('booster', ['gbtree', 'gblinear']),
        'objective': hp.choice('objective', ["reg:squarederror"]),
        'random_state': 42,
        'colsample_bytree': hp.uniform('colsample_bytree', 0.5, 1),
        'gamma': hp.uniform('gamma', 0.2, 0.35),
        'learning_rate': hp.loguniform('learning_rate', np.log(0.005), np.log(0.03)),
        'max_depth': scope.int(hp.quniform('max_depth', 7, 13, 1)),
        'n_estimators': scope.int(hp.quniform('n_estimators', 700, 1400, 100)),
        'subsample': hp.uniform('subsample', 0.4, 1),
        'verbosity': 0,
    }

    trials = Trials()
    best = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=max_evals, trials=trials)

    return best

def build_training_features(data):
    extra_features = ['day_of_week', 'number_of_week', 'delivery_hour']
    totals_columns = ['lint_item_count', 'total_quantity', 'positions', 'total_weight']
    cat_columns = [col for col in data.columns if col.startswith('cat_')]

    filtered_columns = cat_columns + totals_columns + extra_features

    return filtered_columns

def run(data):
    target_columns = ['deep_frozen_bags' , 'cold_bags', 'bags']

    result = {}
    for hub_id in [1, 4]:
        print("hub ", hub_id)
        for target_column_prefix in target_columns:
            df = data_for_target(data, target_column_prefix, hub_id)
            target_column_name, _ = build_names(target_column_prefix)
            target = [target_column_name]

            best_params = hpo(df, target, hub_id)
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
