import boto3
import pandas as pd

def dynamodb_to_dataframe(table_name):
    # Создание клиента DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # Получение всех данных из таблицы
    response = table.scan()
    data = response['Items']

    # Получение всех данных, если они разбиты на страницы
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    # Преобразование данных в DataFrame
    df = pd.DataFrame(data)

    return df

def reorder_columns(df):
    new_columns = ['order_id']
    for i in range(1, 11):
        new_columns.extend([
            f'cat_{i:02}_normal_vu', f'cat_{i:02}_normal_weight',
            f'cat_{i:02}_cold_vu', f'cat_{i:02}_cold_weight',
            f'cat_{i:02}_frozen_vu', f'cat_{i:02}_frozen_weight'
        ])
    additional_columns = [
        'lint_item_count', 'total_quantity', 'positions', 'total_weight',
        'hub_id', 'delivery_time', 'bags_used', 'bags_used_forecast',
        'cold_bags_used', 'cold_bags_used_forecast', 'deep_frozen_bags_used', 'deep_frozen_bags_used_forecast'
    ]
    new_columns.extend(additional_columns)
    df = df[new_columns]
    return df

def main():
    table_name = 'bags_forecast'
    df = dynamodb_to_dataframe(table_name)
    df = reorder_columns(df)

    print(df.head())  # Вывод первых 5 строк для проверки
    # Сохранение DataFrame в файл CSV (по желанию)
    df.to_csv('dynamodb_data.csv', index=False)

if __name__ == '__main__':
    main()

