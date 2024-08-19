
mlflow:
	docker compose up -d
	bin/mlflow-server.sh &

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
	pipenv run python steps/predict.py


validate: ingest
	pipenv run python steps/validate.py

test:
	pipenv run pytest tests


