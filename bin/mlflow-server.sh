#!/bin/sh

pipenv run mlflow server --host 0.0.0.0 --workers 1 --backend-store-uri postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_ENDPOINT}/${DB_NAME} --default-artifact-root s3://${AWS_BUCKET_NAME}/
