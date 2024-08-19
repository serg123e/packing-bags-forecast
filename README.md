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

- **Postgres**: Our MLflow tracking database (AWS RDS or local)
- **AWS Lambda**: Running the training and inference code
- **AWS EFS**: Storing intermediate data
- **Evidently**: Monitoring data drift and model performance
- **MLflow**: Experimet tracking
- **Pytest**: Testing code

## Project Structure

Here's how we structured our project:

- **data/**: Contains our raw and processed data
- **notebooks/**: Jupyter notebooks for exploration and experimentation
- **src/**: Python Lambda functions for data processing, training, and inference
- **scripts/**: Auxilary Python scripts
- **tests/**: Pytest scripts to ensure our code works as expected
- **models/**: Stored models and related artifacts

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (for local testing and deployment)
- AWS account with necessary permissions (for production environment)

### Installation

1. Clone this repo:
    ```bash
    git lfs install
    git clone https://github.com/serg123e/packing-bags-forecast.git
    cd packing-bags-forecast
    ```

2. Install the required Python packages:
    ```bash
    pip install pipenv --user
    pipenv install
    ```

3. Edit `.env` file for production evironment or keep it as is for local testing and development

4. Run required infrastructure
    ```bash
    docker compose up -d
    ```

5. Check if everything works
    ```bash
    make test
    ```


### Running the Project
  - Locally:


      1. **Load CSV**:
          ```bash
          make db_init
          ```
      2. **Hyperparameter optimization**:
          ```bash
          make mlflow &
          make hpo
          ```

          best parameters will be stored in `data/hpo_*.json` files but you can check the whole experiments track on [mlflow server](https://localhost:5000) and update parameters accordingly in `src/train.py`

      3. **Train models**
         ```bash
         make train
         ```

      4. **Running Inference**:
          ```bash
          make predict
          ```


      5. **Data drift monitoring with Evidently**:
          ```bash
          make validate
          ```

  - On AWS Lambda: Put model files on EFS, deploy the inference script `predict.py` as Lambda and trigger it (automatic deployment not implemented yet)


## Testing

We use Pytest for testing. To run the tests, simply use:
```bash
pytest tests/
```

### Simulation
It's assumed that new data is always being added and updated in the `*_bags_used` columns of our `bags_preciction` table. 

For testing and demonstration, we can use the `next_week.py` script from `scripts/`. 

This script loads data from CSV files into the database, simulating the addition of new data each week.

## License

This project is licensed under the MIT License.

## Contact

Got questions? Drop me a message on [LinkedIn](https://www.linkedin.com/in/sergey-evstegneiev/) or create an issue on GitHub.

---


