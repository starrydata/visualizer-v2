import pytest
from presentation.bokeh_graph_creator import BokehGraphCreator
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LinearAxis
from domain.graph import XYSeries, Graph, Axis, AxisType, AxisRange, XYPoint, XYPoints
from unittest.mock import Mock

@pytest.fixture
def simple_graph():
    x_axis = Axis(property="x", axis_type=AxisType.LINEAR, unit="", axis_range=AxisRange(1, 3))
    y_axis = Axis(property="y", axis_type=AxisType.LINEAR, unit="", axis_range=AxisRange(4, 6))
    xy_points = XYPoints([XYPoint(1, 4, "2024-01-01T00:00:00Z"), XYPoint(2, 5, "2024-01-01T00:00:00Z"), XYPoint(3, 6, "2024-01-01T00:00:00Z")])
    xy_series = XYSeries([xy_points, xy_points, xy_points])  # Mocking multiple series for simplicity
    return Graph(x_axis=x_axis, y_axis=y_axis, data=xy_series)

@pytest.fixture
def mock_graph_data_service(simple_graph):
    mock_service = Mock()
    mock_service.get_merged_graph_data.return_value = simple_graph.data
    return mock_service

@pytest.fixture
def graph_creator(mock_graph_data_service):
    return BokehGraphCreator(graph_data_service=mock_graph_data_service)

def test_create_bokeh_figure(graph_creator, simple_graph):
    fig = graph_creator.create_bokeh_figure(simple_graph.x_axis, simple_graph.y_axis)
    assert isinstance(fig, figure)

# create_bokeh_figureで期待したlabelとrangeとtypeとdata_sourceが設定されていることを確認
def test_create_bokeh_figure_properties(graph_creator, simple_graph):
    fig = graph_creator.create_bokeh_figure(simple_graph.x_axis, simple_graph.y_axis)
    assert fig.xaxis[0].axis_label == "x ()"
    assert fig.yaxis[0].axis_label == "y ()"
    assert fig.x_range.start == 1
    assert fig.x_range.end == 3
    assert fig.y_range.start == 4
    assert fig.y_range.end == 6
    assert isinstance(fig.xaxis[0], LinearAxis)
    assert isinstance(fig.yaxis[0], LinearAxis)

def test_create_bokeh_data_source(graph_creator, simple_graph):
    print(simple_graph.data)
    source = graph_creator.create_bokeh_data_source(simple_graph.data)
    assert "x" in source.data
    assert "y" in source.data
    assert len(source.data["x"]) == 9
    assert len(source.data["y"]) == 9
    assert source.data["x"] == [1, 2, 3, 1, 2, 3, 1, 2, 3]
    assert source.data["y"] == [4, 5, 6, 4, 5, 6, 4, 5, 6]
    assert isinstance(source, ColumnDataSource)
