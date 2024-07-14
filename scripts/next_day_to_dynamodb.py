import json
from decimal import ROUND_HALF_UP, Decimal, getcontext
from datetime import date, datetime, timedelta

import boto3
import pandas as pd

# Configure decimal context for precie rounding,
getcontext().prec = 10  # significant digits, 12.34567890
getcontext().rounding = ROUND_HALF_UP


# Load configuration file
def load_config(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config


# Save configuration file
def save_config(config, config_path):
    with open(config_path, 'w') as file:
        json.dump(config, file)


# Load data from CSV file
def load_data(csv_path):
    data = pd.read_csv(csv_path)
    return data


# Convert numerical columns to Decimal and datetime columns to string
def convert_to_compatible_types(data):
    data['order_id'] = data['order_id'].astype(str)

    for col in data.select_dtypes(include=['float64']).columns:
        data[col] = data[col].apply(
            lambda x: str(round(x, 6)) if pd.notnull(x) else '0'
        )
    for col in data.select_dtypes(include=['datetime64[ns, UTC]']).columns:
        data[col] = data[col].astype(str)
    return data


# Filter data for DynamoDB load
def filter_data(
    data, current_date, yesterday_date=pd.to_datetime(date(2000, 1, 1), utc=True)
):
    data['delivery_time'] = pd.to_datetime(data['delivery_time'], utc=True)
    current_date = pd.to_datetime(current_date, utc=True)

    today_data = data[
        (data['delivery_time'] >= yesterday_date)
        & (data['delivery_time'] < current_date)
    ]
    tomorrow_data = data[
        (data['delivery_time'] >= current_date)
        & (data['delivery_time'] < current_date + timedelta(days=1))
    ]

    tomorrow_data = tomorrow_data.drop(
        columns=[col for col in tomorrow_data.columns if '_used' in col]
    )

    return today_data, tomorrow_data


# Check if DynamoDB table is empty
def is_dynamodb_empty(table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.scan(Limit=1)
    return response['Count'] == 0


def remove_duplicates(data):
    data = data.drop_duplicates(subset=['order_id'])
    return data


# Load data into DynamoDB
def load_to_dynamodb(data, table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # Convert numerical columns to Decimal and datetime columns to string
    data = convert_to_compatible_types(data)
    print(f"before removing duplicates: {data.shape[0]}")
    print(data.head())
    data = remove_duplicates(data)
    print(f"after removing duplicates: {data.shape[0]}")
    print(data.head())

    with table.batch_writer() as batch:
        for _, row in data.iterrows():
            item = row.to_dict()
            print(".", end="")
            batch.put_item(Item=item)

            # batch.put_item(Item=row.to_dict())


# Update configuration date
def update_config_date(config):
    current_date = pd.to_datetime(config['current_date'], utc=True)
    new_date = current_date + timedelta(days=1)
    config['current_date'] = new_date.isoformat()


# Main function
def main():
    config_path = 'next_day.json'
    csv_path = '../dataset/bags_forecast_with_id.csv'
    table_name = 'bags_forecast'

    # Load configuration
    config = load_config(config_path)

    # Load data
    data = load_data(csv_path)
    data.fillna(0.0, inplace=True)

    current_date = pd.to_datetime(config['current_date'])

    # Check if DynamoDB table is empty
    if is_dynamodb_empty(table_name):
        # Load all data until the "current date"
        today_data, _ = filter_data(data, current_date)
        print(f"load all data [begin..{current_date}), {today_data.shape[0]} rows")
        load_to_dynamodb(today_data, table_name)
    else:
        # Filter data for "today" and "tomorrow"
        yesterday_date = current_date - timedelta(days=1)
        today_data, tomorrow_data = filter_data(data, current_date, yesterday_date)
        print(f"load data for today, [{yesterday_date}..{current_date})")
        load_to_dynamodb(today_data, table_name)
        print(f"load data for tomorrow, [{current_date}..{current_date}+1 day)")
        load_to_dynamodb(tomorrow_data, table_name)

    # Update configuration date
    update_config_date(config)
    save_config(config, config_path)


if __name__ == '__main__':
    main()
