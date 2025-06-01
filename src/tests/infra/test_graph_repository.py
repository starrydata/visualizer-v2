import os
import pytest
from unittest.mock import patch
from infra.graph_repository_factory import GraphRepositoryFactory, ApiHostName
from domain.graph import XYPoint
from infra.graph_repository import GraphRepositoryApiStarrydata2

# --- Starrydata2 API 用 ---
def mock_response_property_and_unit():
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

def mock_response_property():
    class MockResponse:
        def raise_for_status(self):
            # This is a mock method for testing, so it does nothing
            pass
        def json(self):
            return {
                "data": {
                    "x": [[10, 20]],
                    "y": [[30, 40]]
                }
            }
    return MockResponse()

def mock_response_property_and_unit_missing_updated_at():
    class MockResponse:
        def raise_for_status(self):
            # This is a mock method for testing, so it does nothing
            pass
        def json(self):
            return {
                "data": {
                    "x": [[0], [1, 2]],
                    "y": [[0], [3, 4]]
                    # "updated_at" intentionally missing
                }
            }
    return MockResponse()

def mock_response_property_missing_updated_at():
    class MockResponse:
        def raise_for_status(self):
            # This is a mock method for testing, so it does nothing
            pass
        def json(self):
            return {
                "data": {
                    "x": [[10, 20]],
                    "y": [[30, 40]]
                    # "updated_at" intentionally missing
                }
            }
    return MockResponse()

# --- Starrydata2 API テスト ---
@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_and_unit_format(mock_get):
    mock_get.return_value = mock_response_property_and_unit()
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
    assert len(xy_series.data[0].data) == 1
    assert xy_series.data[0].data[0].x == 0
    assert xy_series.data[0].data[0].y == 0
    assert len(xy_series.data[1].data) == 2
    assert xy_series.data[1].data[0].x == 1
    assert xy_series.data[1].data[0].y == 3
    assert xy_series.data[1].data[1].x == 2
    assert xy_series.data[1].data[1].y == 4
    assert xy_series.data[0].sid == "sid1"
    assert xy_series.data[0].figure_id == "fig1"
    assert xy_series.data[0].sample_id == "sample1"
    assert xy_series.data[0].composition == "comp1"
    assert xy_series.data[1].sid == "sid2"
    assert xy_series.data[1].figure_id == "fig2"
    assert xy_series.data[1].sample_id == "sample2"
    assert xy_series.data[1].composition == "comp2"

@patch("infra.graph_repository.requests.get")
def test_get_graph_by_property_and_unit_missing_updated_at_raises(mock_get):
    mock_get.return_value = mock_response_property_and_unit_missing_updated_at()
    os.environ["STARRYDATA2_API_XY_DATA"] = "http://dummy"
    repo = GraphRepositoryApiStarrydata2()
    import pydantic
    with pytest.raises(pydantic.ValidationError):
        repo.get_graph_by_property_and_unit(
            "Temperature",
            "Seebeck coefficient",
            "K",
            "V/K"
        )
