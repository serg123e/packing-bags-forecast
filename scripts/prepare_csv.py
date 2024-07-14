import sys

import pandas as pd


def main(csv_file_path):
    # Загружаем CSV-файл
    df = pd.read_csv(csv_file_path)

    # Создаем новые имена колонок
    new_columns = []
    for i in range(1, 11):
        new_columns.extend(
            [
                f'cat_{i:02}_normal_vu',
                f'cat_{i:02}_normal_weight',
                f'cat_{i:02}_cold_vu',
                f'cat_{i:02}_cold_weight',
                f'cat_{i:02}_frozen_vu',
                f'cat_{i:02}_frozen_weight',
            ]
        )
    additional_columns = [
        'lint_item_count',
        'total_quantity',
        'positions',
        'total_weight',
        'hub_id',
        'delivery_time',
        'bags_used',
        'bags_used_forecast',
        'cold_bags_used',
        'cold_bags_used_forecast',
        'deep_frozen_bags_used',
        'deep_frozen_bags_used_forecast',
    ]
    new_columns.extend(additional_columns)

    # Заменяем названия колонок
    df.columns = new_columns

    # Сортируем по колонке delivery_time
    df = df.sort_values(by='delivery_time')

    # Добавляем колонку order_id с уникальными значениями начиная с 10000001
    df['order_id'] = range(100000001, 100000001 + len(df))

    # Перемещаем колонку order_id на первое место
    cols = df.columns.tolist()
    cols = ['order_id'] + [col for col in cols if col != 'order_id']
    df = df[cols]

    # Сохраняем результат в новый CSV-файл
    output_file_path = 'sorted_with_order_id.csv'
    df.to_csv(output_file_path, index=False)
    print(f'Processed and sorted file saved as {output_file_path}')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file_path>")
    else:
        csv_file_path = sys.argv[1]
        main(csv_file_path)
