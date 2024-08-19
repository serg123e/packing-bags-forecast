import pytest
import pandas as pd
from pandas import DataFrame
from transform import transform, extra_features, remove_outliers, do_transform, input_file_path, output_file_path

@pytest.fixture
def sample_data():
    # Sample DataFrame to be used in tests
    return pd.DataFrame({
        'delivery_time': ['2023-08-19 12:00:00', '2023-08-19 13:00:00'],
        'bags_used': [5, 12],
        'cold_bags_used': [1, 0],
        'deep_frozen_bags_used': [0, 1],
        'total_weight': [10000, 60000]
    })

def test_transform(sample_data):
    transformed_data = transform(sample_data.copy())
    assert transformed_data['delivery_time'].dtype == 'datetime64[ns, UTC]'

def test_extra_features(sample_data):
    sample_data['delivery_time'] = pd.to_datetime(sample_data['delivery_time'], utc=True)
    enriched_data = extra_features(sample_data)
    assert 'day_of_year' in enriched_data.columns
    assert 'day_of_week' in enriched_data.columns
    assert 'number_of_week' in enriched_data.columns
    assert 'delivery_hour' in enriched_data.columns
    assert enriched_data['day_of_year'].iloc[0] == enriched_data['delivery_time'].dt.dayofyear.iloc[0]

def test_remove_outliers(sample_data):
    sample_data['delivery_time'] = pd.to_datetime(sample_data['delivery_time'], utc=True)
    print(sample_data)
    filtered_data = remove_outliers(sample_data)
    print(filtered_data)
    assert filtered_data['bags_used'].max() < 10
    assert filtered_data['cold_bags_used'].min() >= 0
    assert filtered_data['deep_frozen_bags_used'].min() >= 0
    assert filtered_data['total_weight'].max() < 50000

if __name__ == '__main__':
    pytest.main()
