
mlflow:
	docker compose up -d

ingest:
	dotenv run pipenv run python steps/download.py
	dotenv run pipenv run python steps/ingest.py

prepare: ingest
	dotenv run pipenv run python steps/transform.py

train:	prepare
	dotenv run pipenv run python steps/train.py

hpo:    prepare
	dotenv run pipenv run python steps/hpo_xgboost.py
	dotenv run pipenv run python steps/hpo_randomforest.py

predict:
	dotenv run pipenv run python steps/predict.py


validate: ingest
	dotenv run pipenv run python steps/validate.py

test:
	pytest tests


