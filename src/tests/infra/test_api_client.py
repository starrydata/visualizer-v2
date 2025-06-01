import pytest
from infra.api_client import XYApiResponse, Starrydata2ApiClient, CleansingDatasetApiClient
from unittest.mock import patch

# --- Starrydata2ApiClient ---
def test_starrydata2_api_client_fetch_xy_data_success():
    mock_json = {
        "data": {
            "x": [[1.0, 2.0], [3.0]],
            "y": [[10.0, 20.0], [30.0]],
            "updated_at": ["2025-06-01T00:00:00Z", "2025-06-01T01:00:00Z"],
            "SID": ["sid1", "sid2"],
            "figure_id": ["fig1", "fig2"],
            "sample_id": ["sample1", "sample2"],
            "composition": ["comp1", "comp2"]
        }
    }
    class MockResponse:
        def raise_for_status(self):
            # This is a mock method for testing, so it does nothing
            pass
        def json(self):
            return mock_json
    with patch("requests.get", return_value=MockResponse()):
        client = Starrydata2ApiClient("http://dummy")
        params = {"property_x": "x", "property_y": "y"}
        result = client.fetch_xy_data(params)
        assert isinstance(result, XYApiResponse)
        assert result.x == [[1.0, 2.0], [3.0]]
        assert result.y == [[10.0, 20.0], [30.0]]
        assert result.updated_at == ["2025-06-01T00:00:00Z", "2025-06-01T01:00:00Z"]
        assert result.SID == ["sid1", "sid2"]
        assert result.figure_id == ["fig1", "fig2"]
        assert result.sample_id == ["sample1", "sample2"]
        assert result.composition == ["comp1", "comp2"]

# --- CleansingDatasetApiClient ---
def test_cleansing_dataset_api_client_fetch_xy_data_success():
    mock_json = {
        "data": {
            "x": [[5.0, 6.0]],
            "y": [[50.0, 60.0]],
            "updated_at": ["2025-06-01T02:00:00Z"],
            "SID": ["sid3"],
            "figure_id": ["fig3"],
            "sample_id": ["sample3"],
            "composition": ["comp3"]
        }
    }
    class MockResponse:
        def raise_for_status(self):
            # This is a mock method for testing, so it does nothing
            pass
        def json(self):
            return mock_json
    with patch("requests.get", return_value=MockResponse()):
        client = CleansingDatasetApiClient("http://dummy")
        result = client.fetch_xy_data("x", "y")
        assert isinstance(result, XYApiResponse)
        assert result.x == [[5.0, 6.0]]
        assert result.y == [[50.0, 60.0]]
        assert result.updated_at == ["2025-06-01T02:00:00Z"]
        assert result.SID == ["sid3"]
        assert result.figure_id == ["fig3"]
        assert result.sample_id == ["sample3"]
        assert result.composition == ["comp3"]

# --- Error cases ---
def test_starrydata2_api_client_invalid_response():
    # missing required fields
    mock_json = {"data": {"x": [[1.0]], "y": [[2.0]]}}  # missing updated_at, SID, figure_id, sample_id, composition
    class MockResponse:
        def raise_for_status(self):
            # This is a mock method for testing, so it does nothing
            pass
        def json(self):
            return mock_json
    with patch("requests.get", return_value=MockResponse()):
        client = Starrydata2ApiClient("http://dummy")
        params = {"property_x": "x", "property_y": "y"}
        with pytest.raises(Exception):
            client.fetch_xy_data(params)

def test_cleansing_dataset_api_client_invalid_response():
    # missing required fields
    mock_json = {"data": {"x": [[1.0]], "y": [[2.0]]}}  # missing updated_at, SID, figure_id, sample_id, composition
    class MockResponse:
        def raise_for_status(self):
            # This is a mock method for testing, so it does nothing
            pass
        def json(self):
            return mock_json
    with patch("requests.get", return_value=MockResponse()):
        client = CleansingDatasetApiClient("http://dummy")
        with pytest.raises(Exception):
            client.fetch_xy_data("x", "y")
