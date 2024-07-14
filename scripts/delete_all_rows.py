import boto3


def delete_all_items(table_name):
    # Создание клиента DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # Сканирование таблицы для получения всех элементов
    response = table.scan()
    data = response['Items']

    # Получение всех данных, если они разбиты на страницы
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    # Удаление всех элементов
    with table.batch_writer() as batch:
        for item in data:
            batch.delete_item(Key={'order_id': item['order_id']})
    print(f"Deleted {len(data)} items from {table_name}")


def main():
    table_name = 'bags_forecast'
    delete_all_items(table_name)


if __name__ == '__main__':
    main()
