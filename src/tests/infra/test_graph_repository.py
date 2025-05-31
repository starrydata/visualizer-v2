import os
import pytest
from unittest.mock import patch
from domain.material_type import MaterialType
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
    repo = GraphRepositoryFactory.create(ApiHostName.CLEANSING_DATASET)
    graph = repo.get_graph_by_property(MaterialType.THERMOELECTRIC, "Temperature", "Seebeck coefficient")
    assert graph is not None
    assert len(graph.data_point_series) == 2
    assert len(graph.data_point_series[0].data_points) == 3
    assert pytest.approx(graph.data_point_series[0].data_points[0].x, 0.001) == 299.8597
    assert pytest.approx(graph.data_point_series[0].data_points[0].y, 0.001) == -148.4452
    assert len(graph.data_point_series[1].data_points) == 2
    assert graph.data_point_series[1].data_points[0].x == 1
    assert graph.data_point_series[1].data_points[0].y == 10

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_not_found(mock_get, mock_response):
    mock_get.return_value = mock_response
    os.environ["STARRYDATA_BULK_DATA_API"] = "http://dummy"
    repo = GraphRepositoryFactory.create(ApiHostName.CLEANSING_DATASET)
    with pytest.raises(ValueError) as excinfo:
        repo.get_graph_by_property(MaterialType.THERMOELECTRIC, "NotExist", "Seebeck coefficient")
    assert "not found" in str(excinfo.value)

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_invalid_material_type(mock_get, mock_response):
    mock_get.return_value = mock_response
    os.environ["STARRYDATA_BULK_DATA_API"] = "http://dummy"
    repo = GraphRepositoryFactory.create(ApiHostName.CLEANSING_DATASET)
    class DummyMaterialType:
        pass
    with pytest.raises(ValueError) as excinfo:
        repo.get_graph_by_property(DummyMaterialType(), "Temperature", "Seebeck coefficient")
    assert "Unknown material_type" in str(excinfo.value)

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_empty_data(mock_get, mock_response):
    class EmptyMockResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {"data": {"x": [], "y": []}}
    mock_get.return_value = EmptyMockResponse()
    os.environ["STARRYDATA_BULK_DATA_API"] = "http://dummy"
    repo = GraphRepositoryFactory.create(ApiHostName.CLEANSING_DATASET)
    graph = repo.get_graph_by_property(MaterialType.THERMOELECTRIC, "Temperature", "Seebeck coefficient")
    assert graph is not None
    assert len(graph.data_point_series) == 0
