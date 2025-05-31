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
    # property_x, property_y, unit_x, unit_y のみ渡す
    data_points_list = repo.get_graph_by_property_and_unit(
        "Temperature",
        "Seebeck coefficient",
        "K",
        "V/K"
    )
    assert data_points_list is not None
    assert len(data_points_list) == 2
    assert len(data_points_list[0].data_points) == 1
    assert data_points_list[0].data_points[0].x == 0
    assert data_points_list[0].data_points[0].y == 0
    assert len(data_points_list[1].data_points) == 2
    assert data_points_list[1].data_points[0].x == 1
    assert data_points_list[1].data_points[0].y == 3
    assert data_points_list[1].data_points[1].x == 2
    assert data_points_list[1].data_points[1].y == 4

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_format(mock_get):
    mock_get.return_value = mock_response_property()
    os.environ["STARRYDATA_BULK_DATA_API"] = "http://dummy"
    from infra.graph_repository import GraphRepositoryApiCleansingDataset
    repo = GraphRepositoryApiCleansingDataset()
    # property_x, property_y のみ渡す
    data_points_list = repo.get_graph_by_property("Temperature", "Seebeck coefficient")
    assert data_points_list is not None
    assert len(data_points_list) == 1
    assert [p.x for p in data_points_list[0].data_points] == [10, 20]
    assert [p.y for p in data_points_list[0].data_points] == [30, 40]

