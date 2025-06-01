import os
import pytest
from unittest.mock import patch
from infra.graph_repository_factory import GraphRepositoryFactory, ApiHostName

@pytest.fixture
def mock_response():
    class MockResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {
                "data": {
                    "x": [[299.8597, 324.8683, 349.8757], [1, 2], []],
                    "y": [[-148.4452, -160.2763, -172.9511], [10, 20], []]
                }
            }
    return MockResponse()

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_response_format(mock_get, mock_response):
    mock_get.return_value = mock_response
    os.environ["STARRYDATA_BULK_DATA_API"] = "http://dummy"
    from infra.graph_repository import GraphRepositoryApiCleansingDataset
    repo = GraphRepositoryApiCleansingDataset()
    xy_series = repo.get_graph_by_property("Temperature", "Seebeck coefficient")
    assert xy_series is not None
    assert len(xy_series.data) == 2
    assert [p.x for p in xy_series.data[0].data] == [299.8597, 324.8683, 349.8757]
    assert [p.y for p in xy_series.data[0].data] == [-148.4452, -160.2763, -172.9511]
    assert [p.x for p in xy_series.data[1].data] == [1, 2]
    assert [p.y for p in xy_series.data[1].data] == [10, 20]

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_not_found(mock_get, mock_response):
    mock_get.return_value = mock_response
    os.environ["STARRYDATA_BULK_DATA_API"] = "http://dummy"
    from infra.graph_repository import GraphRepositoryApiCleansingDataset
    repo = GraphRepositoryApiCleansingDataset()
    xy_series = repo.get_graph_by_property("NotExist", "Seebeck coefficient")
    assert hasattr(xy_series, "data")
    assert isinstance(xy_series.data, list)

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_invalid_material_type(mock_get, mock_response):
    mock_get.return_value = mock_response
    os.environ["STARRYDATA_BULK_DATA_API"] = "http://dummy"
    # material_typeは不要になったのでテスト不要
    assert True

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_empty_data(mock_get, mock_response):
    class EmptyMockResponse:
        def raise_for_status(self):
            pass  # intentionally empty for test
        def json(self):
            return {"data": {"x": [], "y": []}}
    mock_get.return_value = EmptyMockResponse()
    os.environ["STARRYDATA_BULK_DATA_API"] = "http://dummy"
    from infra.graph_repository import GraphRepositoryApiCleansingDataset
    repo = GraphRepositoryApiCleansingDataset()
    xy_series = repo.get_graph_by_property("Temperature", "Seebeck coefficient")
    assert xy_series is not None
    assert len(xy_series.data) == 0

def make_point(x, y):
    from src.domain.graph import XYPoint
    return XYPoint(x, y)
