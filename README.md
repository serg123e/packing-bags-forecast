# Bag Prediction Project

Hey there! Welcome to our Bag Prediction Project. 
Our aim here is to predict the number of bags needed to pack orders for the next day's delivery. 
We don't have the exact volume of the products, 
but we do know their categories (like Grocery, Fresh meat, Wine, Deep frozen products, etc.), the quantity, and the weight.

## Project Overview

Every day, orders are packed and delivered, and we keep track of how many bags of each type (normal, cold, deep frozen) are required. 
This data helps us predict the number of bags needed for the next day's deliveries. 
Accurate predictions are crucial for planning logistics and understanding the required number of cars.

## Tech Stack

Here's what we're using:

- **AWS RDS**: Our MLflow tracking database
- **AWS Lambda**: Running the inference code
- **Evidently**: Monitoring model performance
- **Grafana**: Visualizing the monitoring metrics
- **MLflow**: Managing the machine learning lifecycle
- **Pytest**: Testing our code

## Project Structure

Here's how we structured our project:

- **data/**: Contains our raw and processed data
- **notebooks/**: Jupyter notebooks for exploration and experimentation
- **scripts/**: Python scripts for data processing, training, and inference
- **tests/**: Pytest scripts to ensure our code works as expected
- **models/**: Stored models and related artifacts
- **monitoring/**: Scripts and configurations for monitoring with Evidently and Grafana

## Getting Started

### Prerequisites

- AWS account with necessary permissions
- Python 3.8+
- Docker (for local testing and deployment)

### Installation

1. Clone this repo:
    ```bash
    git clone https://github.com/yourusername/bag-prediction-project.git
    cd bag-prediction-project
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Setting Up AWS

1. Set up an RDS instance for MLflow tracking.
2. Configure AWS Lambda to run the inference code.
3. Set up AWS credentials and permissions.

### Running the Project

1. **Data Processing**:
    ```bash
    python scripts/data_processing.py
    ```

2. **Training the Model**:
    ```bash
    python scripts/train_model.py
    ```

3. **Running Inference**:
    - Locally:
        ```bash
        python scripts/inference.py
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

Got questions? Drop me a message on [LinkedIn](https://www.linkedin.com/in/yourprofile) or create an issue on GitHub.

---

Enjoy predicting those bags! 🚀
