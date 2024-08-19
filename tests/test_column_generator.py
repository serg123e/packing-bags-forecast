import pytest
import pandas as pd
from column_generator import generate_columns, get_column_names, build_training_features

TOTAL_COLUMNS = 10 * 6 + 13


def test_generate_columns():
    columns = generate_columns()

    # Test the correct number of columns
    assert (
        len(columns) == TOTAL_COLUMNS
    ), f"Expected {TOTAL_COLUMNS} columns, but got {len(columns)}"

    # Test the first and last elements to ensure correct generation
    assert columns[0] == 'order_id INTEGER PRIMARY KEY'
    assert columns[-1] == 'deep_frozen_bags_used_forecast FLOAT'

    # Test a sample of generated columns to check the format
    expected_sample = [
        'cat_01_normal_vu FLOAT',
        'cat_01_cold_vu FLOAT',
        'cat_10_frozen_weight FLOAT',
    ]
    assert all(
        col in columns for col in expected_sample
    ), "Generated columns do not match the expected format"


def test_get_column_names():
    column_names = get_column_names()

    # Check that the names are correctly extracted
    assert column_names[0] == 'order_id'
    assert column_names[-1] == 'deep_frozen_bags_used_forecast'

    # Check the total number of column names
    assert (
        len(column_names) == TOTAL_COLUMNS
    ), f"Expected {TOTAL_COLUMNS} column names, but got {len(column_names)}"


def test_build_training_features():
    # Create a mock DataFrame that simulates the structure of the data
    data_columns = [
        'cat_01_normal_vu',
        'cat_01_cold_weight',
        'cat_01_frozen_vu',
        'lint_item_count',
        'total_quantity',
        'positions',
        'total_weight',
        'day_of_week',
        'number_of_week',
        'delivery_hour',
        'unrelated_column',
    ]

    training_features = build_training_features(data_columns)

    # Expected columns in the output
    expected_columns = [
        'cat_01_normal_vu',
        'cat_01_cold_weight',
        'cat_01_frozen_vu',
        'lint_item_count',
        'total_quantity',
        'positions',
        'total_weight',
        'day_of_week',
        'number_of_week',
        'delivery_hour',
    ]

    assert sorted(training_features) == sorted(
        expected_columns
    ), f"Expected columns {expected_columns}, but got {training_features}"

    # Ensure no unrelated columns are included
    assert (
        'unrelated_column' not in training_features
    ), "Unrelated columns should not be included in the training features"


if __name__ == '__main__':
    pytest.main()
