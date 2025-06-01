import pytest
from presentation.bokeh_graph_creator import BokehGraphCreator
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LinearAxis
from domain.graph import Axis, AxisType, AxisRange, XYPoint, XYPoints
from application.graph_data_service import XYPointsDTO, XYPointsListDTO
from unittest.mock import Mock

@pytest.fixture
def x_axis():
    return Axis(property="x", axis_type=AxisType.LINEAR, unit="", axis_range=AxisRange(1, 3))

@pytest.fixture
def y_axis():
    return Axis(property="y", axis_type=AxisType.LINEAR, unit="", axis_range=AxisRange(4, 6))

@pytest.fixture
def simple_dto():
    xy_points = XYPoints([XYPoint(1, 4), XYPoint(2, 5), XYPoint(3, 6)], updated_at="2024-01-01T00:00:00Z")
    dto = XYPointsDTO(data=xy_points.data, is_highlighted=False)
    dto_list = XYPointsListDTO(data=[dto, dto, dto])  # Mocking multiple series for simplicity
    return dto_list

@pytest.fixture
def mock_graph_data_service(simple_dto):
    mock_service = Mock()
    mock_service.get_merged_graph_data.return_value = simple_dto
    return mock_service

@pytest.fixture
def graph_creator(mock_graph_data_service):
    return BokehGraphCreator(graph_data_service=mock_graph_data_service)

def test_create_bokeh_figure(graph_creator, x_axis, y_axis):
    fig = graph_creator.create_bokeh_figure(x_axis, y_axis)
    assert isinstance(fig, figure)

def test_create_bokeh_figure_properties(graph_creator, x_axis, y_axis):
    fig = graph_creator.create_bokeh_figure(x_axis, y_axis)
    assert fig.xaxis[0].axis_label == "x ()"
    assert fig.yaxis[0].axis_label == "y ()"
    assert fig.x_range.start == 1
    assert fig.x_range.end == 3
    assert fig.y_range.start == 4
    assert fig.y_range.end == 6
    assert isinstance(fig.xaxis[0], LinearAxis)
    assert isinstance(fig.yaxis[0], LinearAxis)

def test_create_bokeh_data_source(graph_creator, simple_dto):
    source = graph_creator.create_bokeh_data_source(simple_dto)
    assert "x" in source.data
    assert "y" in source.data
    assert len(source.data["x"]) == 9
    assert len(source.data["y"]) == 9
    assert source.data["x"] == [1, 2, 3, 1, 2, 3, 1, 2, 3]
    assert source.data["y"] == [4, 5, 6, 4, 5, 6, 4, 5, 6]
    assert isinstance(source, ColumnDataSource)
