
mlflow:
	docker compose up -d
	bin/mlflow-server.sh &

ingest:
	dotenv run pipenv run python src/download.py
	dotenv run pipenv run python src/ingest.py

prepare: ingest
	dotenv run pipenv run python src/transform.py

train:	prepare
	dotenv run pipenv run python src/train.py

hpo:    prepare
	dotenv run pipenv run python src/hpo_xgboost.py
	dotenv run pipenv run python src/hpo_randomforest.py

predict:
	dotenv run pipenv run python steps/predict.py


validate: ingest
	dotenv run pipenv run python steps/validate.py

test:
	pytest tests


