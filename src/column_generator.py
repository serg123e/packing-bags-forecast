# column_generator.py

def generate_columns():
    # Define the base structure of the columns
    columns = ['order_id INTEGER PRIMARY KEY']
    for i in range(1, 11):
        columns.extend(
            [
                f'cat_{i:02}_normal_vu FLOAT',
                f'cat_{i:02}_normal_weight FLOAT',
                f'cat_{i:02}_cold_vu FLOAT',
                f'cat_{i:02}_cold_weight FLOAT',
                f'cat_{i:02}_frozen_vu FLOAT',
                f'cat_{i:02}_frozen_weight FLOAT',
            ]
        )
    additional_columns = [
        'lint_item_count INTEGER',
        'total_quantity INTEGER',
        'positions INTEGER',
        'total_weight FLOAT',
        'hub_id INTEGER',
        'delivery_time TIMESTAMP',
        'bags_used INTEGER',
        'bags_used_forecast FLOAT',
        'cold_bags_used INTEGER',
        'cold_bags_used_forecast FLOAT',
        'deep_frozen_bags_used INTEGER',
        'deep_frozen_bags_used_forecast FLOAT',
    ]
    columns.extend(additional_columns)
    return columns


def get_column_names():
    columns = [col.split()[0] for col in generate_columns()]
    return columns


def build_training_features(data):
    extra_features = ['day_of_week', 'number_of_week', 'delivery_hour']
    totals_columns = ['lint_item_count', 'total_quantity', 'positions', 'total_weight']
    cat_columns = [col for col in data.columns if col.startswith('cat_')]

    filtered_columns = cat_columns + totals_columns + extra_features

    return filtered_columns
