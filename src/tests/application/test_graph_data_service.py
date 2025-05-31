import pytest
from application.graph_data_service import GraphDataService
from unittest.mock import patch, MagicMock
from domain.graph import DataPoints, DataPointsSeries, DataPoint

@pytest.fixture
def mock_bulk_data_series():
    # bulk側のDataPointsSeries
    return DataPointsSeries(data=[DataPoints([DataPoint(1, 2), DataPoint(3, 4)])])

@pytest.fixture
def mock_today_data_series():
    # today側のDataPointsSeries
    return DataPointsSeries(data=[DataPoints([DataPoint(5, 6)])])

@patch("infra.graph_repository_factory.GraphRepositoryFactory.create")
def test_get_merged_graph_data(mock_factory, mock_bulk_data_series, mock_today_data_series):
    # 1回目はbulk, 2回目はtoday
    mock_bulk_repo = MagicMock()
    mock_bulk_repo.get_graph_by_property.return_value = mock_bulk_data_series
    mock_today_repo = MagicMock()
    mock_today_repo.get_graph_by_property_and_unit.return_value = mock_today_data_series
    mock_factory.side_effect = [mock_bulk_repo, mock_today_repo]
    service = GraphDataService()
    merged = service.get_merged_graph_data(
        prop_x="Temperature",
        prop_y="Seebeck coefficient",
        unit_x="K",
        unit_y="V/K",
    )
    # bulk + today のDataPointsSeriesリストが結合されていること
    assert isinstance(merged, DataPointsSeries)
    assert len(merged.data) == 2
    assert merged.data[0] == mock_bulk_data_series.data[0]
    assert merged.data[1] == mock_today_data_series.data[0]
