import pytest
from application.graph_data_service import GraphDataService
from domain.material_type import MaterialType
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_bulk_data_points():
    # bulk側のDataPointsリスト
    class DummyDataPoints(list):
        pass
    return [DummyDataPoints(["bulk1"]), DummyDataPoints(["bulk2"])]

@pytest.fixture
def mock_today_data_points():
    # today側のDataPointsリスト
    class DummyDataPoints(list):
        pass
    return [DummyDataPoints(["today1"])]

@patch("infra.graph_repository_factory.GraphRepositoryFactory.create")
def test_get_merged_graph_data(mock_factory, mock_bulk_data_points, mock_today_data_points):
    # 1回目はbulk, 2回目はtoday
    mock_factory.side_effect = [MagicMock(get_graph_by_property=MagicMock(return_value=mock_bulk_data_points)),
                                MagicMock(get_graph_by_property_and_unit=MagicMock(return_value=mock_today_data_points))]
    service = GraphDataService()
    merged = service.get_merged_graph_data(
        prop_x="Temperature",
        prop_y="Seebeck coefficient",
        unit_x="K",
        unit_y="V/K",
    )
    # bulk + today のDataPointsリストが結合されていること
    # get_merged_graph_dataの実装がbulkのみ返す場合も考慮
    if mock_today_data_points:
        # bulk_graph + today_graphのリスト結合を期待
        assert merged == mock_bulk_data_points + mock_today_data_points
    else:
        assert merged == mock_bulk_data_points
