
mlflow:
	docker compose up -d
	dotenv bin/mlflow-server.sh

db_init:
	pipenv run python src/upload_csv.py

db_test_init:
	pipenv run python src/upload_csv.py tests/test.csv

ingest:
	pipenv run python src/download.py
	pipenv run python src/ingest.py

prepare: ingest
	pipenv run python src/transform.py

train:	prepare
	pipenv run python src/train.py

hpo:    prepare
	pipenv run python src/hpo_xgboost.py
	pipenv run python src/hpo_randomforest.py

predict:
	pipenv run python src/predict.py


validate: ingest
	pipenv run python src/validate.py

test:
	pipenv run pytest tests


