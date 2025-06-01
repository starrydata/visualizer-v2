import pytest
from application.graph_data_service import GraphDataService, XYSeriesDTO, XYPointsDTO
from unittest.mock import patch, MagicMock
from src.tests.domain.graph_mock_factory import make_xy_points, make_xy_series

def make_point(x, y):
    from domain.graph import XYPoint
    return XYPoint(x, y)

@pytest.fixture
def mock_bulk_data_series():
    # bulk側のDataPointsSeries
    return make_xy_series([make_xy_points([make_point(1, 2), make_point(3, 4)], updated_at="2024-01-01T00:00:00Z")])

@pytest.fixture
def mock_today_data_series():
    # today側のDataPointsSeries
    return make_xy_series([make_xy_points([make_point(5, 6)], updated_at="2024-01-02T00:00:00Z")])

@patch("infra.graph_repository_factory.GraphRepositoryFactory.create")
def test_get_merged_graph_data(mock_factory, mock_bulk_data_series, mock_today_data_series):
    # 1回目はbulk, 2回目はtoday
    mock_bulk_repo = MagicMock()
    mock_bulk_repo.get_graph_by_property.return_value = mock_bulk_data_series
    mock_today_repo = MagicMock()
    mock_today_repo.get_graph_by_property_and_unit.return_value = mock_today_data_series
    mock_factory.side_effect = [mock_bulk_repo, mock_today_repo]
    service = GraphDataService()
    merged: XYSeriesDTO = service.get_merged_graph_data(
        prop_x="Temperature",
        prop_y="Seebeck coefficient",
        unit_x="K",
        unit_y="V/K",
    )
    # bulk + today のXYPointsDTOリストが結合されていること
    assert isinstance(merged, XYSeriesDTO)
    assert len(merged.data) == 2
    assert merged.data[0].data == mock_bulk_data_series.data[0].data
    assert merged.data[1].data == mock_today_data_series.data[0].data
    assert merged.data[0].is_highlighted is False
    assert merged.data[1].is_highlighted is False
