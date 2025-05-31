import os
import pytest
from unittest.mock import patch
from domain.material_type import MaterialType
from infra.graph_repository import GraphRepositoryApiStarrydata2

def mock_response_property_and_unit():
    class MockResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {
                "data": {
                    "x": [[0], [1, 2]],
                    "y": [[0], [3, 4]],
                    "SID": ["sid1", "sid2"],
                    "figure_id": ["fig1", "fig2"],
                    "sample_id": ["sample1", "sample2"],
                    "composition": ["comp1", "comp2"],
                    "updated_at": ["2025-05-30T10:02:26.505Z", "2025-05-30T10:02:26.505Z"]
                }
            }
    return MockResponse()

def mock_response_property():
    class MockResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {
                "data": {
                    "x": [[10, 20]],
                    "y": [[30, 40]]
                }
            }
    return MockResponse()

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_and_unit_format(mock_get):
    mock_get.return_value = mock_response_property_and_unit()
    os.environ["STARRYDATA2_API_XY_DATA"] = "http://dummy"
    repo = GraphRepositoryApiStarrydata2()
    graph = repo.get_graph_by_property_and_unit(
        MaterialType.THERMOELECTRIC,
        property_x="Temperature",
        property_y="Seebeck coefficient",
        unit_x="K",
        unit_y="V/K",
        date_from="2025-01-01T00:00:00Z",
        date_to="2025-12-31T23:59:59Z",
        limit=10
    )
    assert graph is not None
    assert len(graph.data_point_series) == 2
    assert len(graph.data_point_series[0].data_points) == 1
    assert graph.data_point_series[0].data_points[0].x == 0
    assert graph.data_point_series[0].data_points[0].y == 0
    assert len(graph.data_point_series[1].data_points) == 2
    assert graph.data_point_series[1].data_points[0].x == 1
    assert graph.data_point_series[1].data_points[0].y == 3
    assert graph.data_point_series[1].data_points[1].x == 2
    assert graph.data_point_series[1].data_points[1].y == 4

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_format(mock_get):
    mock_get.return_value = mock_response_property()
    os.environ["STARRYDATA_BULK_DATA_API"] = "http://dummy"
    repo = GraphRepositoryApiStarrydata2()
    graph = repo.get_graph_by_property(MaterialType.THERMOELECTRIC, "Temperature", "Seebeck coefficient")
    assert graph is None

