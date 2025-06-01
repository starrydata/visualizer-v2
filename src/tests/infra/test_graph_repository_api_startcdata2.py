import os
import pytest
from unittest.mock import patch, MagicMock
from domain.material_type import MaterialType
from infra.graph_repository import GraphRepositoryApiStarrydata2
from src.tests.domain.graph_mock_factory import make_xy_points
from src.domain.graph import XYPoint

def mock_response():
    class MockResponse:
        def raise_for_status(self):
            # This is a mock method for testing, so it does nothing
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

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_and_unit_format(mock_get):
    mock_get.return_value = mock_response()
    os.environ["STARRYDATA2_API_XY_DATA"] = "http://dummy"
    repo = GraphRepositoryApiStarrydata2()
    xy_series = repo.get_graph_by_property_and_unit(
        "Temperature",
        "Seebeck coefficient",
        "K",
        "V/K"
    )
    assert xy_series is not None
    assert len(xy_series.data) == 2
    assert [p.x for p in xy_series.data[0].data] == [0]
    assert [p.y for p in xy_series.data[0].data] == [0]
    assert [p.x for p in xy_series.data[1].data] == [1, 2]
    assert [p.y for p in xy_series.data[1].data] == [3, 4]
