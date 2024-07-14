# Bag Prediction Project

Hey there! Welcome to our Bag Prediction Project. 
Our aim here is to predict the number of bags needed to pack orders for the next day's delivery. 
We don't have the exact volume of the products, 
but we do know their categories (like Grocery, Fresh meat, Wine, Deep frozen products, etc.), the quantity in standartized Volume Units, and the weight.

## Project Overview

Every day, orders are packed and delivered, and we keep track of how many bags of each type (normal, cold, deep frozen) are required. 
This data helps us predict the number of bags needed for the next day's deliveries. 
Accurate predictions are crucial for planning logistics and understanding the required number of cars.

## Tech Stack

Here's what we're using:

- **AWS RDS**: Our MLflow tracking database
- **AWS Lambda**: Running the training and inference code
- **AWS EFS**: Storing intermediate data
- **Evidently**: Monitoring data drift and model performance
- **MLflow**: Experimet tracking
- **Pytest**: Testing code

## Project Structure

Here's how we structured our project:

- **data/**: Contains our raw and processed data
- **notebooks/**: Jupyter notebooks for exploration and experimentation
- **steps/**: Python Lambda functions for data processing, training, and inference
- **scripts/**: Auxilary Python scripts
- **tests/**: Pytest scripts to ensure our code works as expected
- **models/**: Stored models and related artifacts
- **monitoring/**: Scripts and configurations for monitoring with Evidently and Grafana

## Getting Started

### Prerequisites

- AWS account with necessary permissions
- Python 3.10+
- Docker (for local testing and deployment)

### Installation

1. Clone this repo:
    ```bash
    git clone https://github.com/serg123e/packing-bags-forecast.git
    cd packing-bags-forecast
    ```

2. Install the required Python packages:
    ```bash
    pipenv install
    ```

3. Edit `.env` file

### Setting Up AWS

1. Set up an RDS instance for MLflow tracking.
2. Configure AWS Lambda to run the inference code.
3. Set up AWS credentials and permissions.


### Simulation
It's assumed that new data is always being added and updated in the `*_bags_used` columns of our `data_warehouse` database. 

For testing and demonstration, we can use the `next_week.py` script from `scripts/`. 

This script loads data from CSV files into the database, simulating the addition of new data each week.


### Spin up mlflow server:
```bash
make mlflow
```


### Running the Project
  - Locally:

      1. **Data Processing**:
          ```bash
          pipenv run python steps/download.py
          pipenv run python steps/ingest.py
          pipenv run python steps/transform.py
          ```

      2. **Hyperparameter optimization**:
          ```bash
          pipenv run python steps/hpo_xgboost.py
          pipenv run python steps/hpo_randomforest.py
          ```

      3. **Running Inference**:
          ```bash
          pipenv run steps/predict.py
          ```

  - On AWS Lambda: Deploy the inference script to Lambda and trigger it.

4. **Monitoring**:
    - Set up Evidently and Grafana using the provided configurations in the `monitoring/` folder.
    - Start the monitoring services to visualize the model's performance.

## Testing

We use Pytest for testing. To run the tests, simply use:
```bash
pytest tests/
```

## Contributions

Feel free to fork this repo, make your changes, and submit a pull request. Any contributions to improve the project are welcome!

## License

This project is licensed under the MIT License.

## Contact

Got questions? Drop me a message on [LinkedIn](https://www.linkedin.com/in/sergey-evstegneiev/) or create an issue on GitHub.

---

Enjoy predicting those bags! 🚀

