import pytest
from presentation.bokeh_graph_creator import BokehGraphCreator
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LinearAxis
from domain.graph import Graph, Axis, AxisType, AxisRange, DataPoint, DataPoints
from unittest.mock import Mock

@pytest.fixture
def mock_graph_data_service(simple_graph):
    mock_service = Mock()
    mock_service.get_merged_graph_data.return_value = simple_graph
    return mock_service

@pytest.fixture
def graph_creator(mock_graph_data_service):
    return BokehGraphCreator(graph_data_service=mock_graph_data_service)

@pytest.fixture
def simple_graph():
    x_axis = Axis(property="x", axis_type=AxisType.LINEAR, unit="", axis_range=AxisRange(1, 3))
    y_axis = Axis(property="y", axis_type=AxisType.LINEAR, unit="", axis_range=AxisRange(4, 6))
    data_points = [DataPoint(1, 4), DataPoint(2, 5), DataPoint(3, 6)]
    data_point_series = [DataPoints(data_points)]
    return Graph(x_axis=x_axis, y_axis=y_axis, data_point_series=data_point_series)

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
    source = graph_creator.create_bokeh_data_source(simple_graph)
    assert "x" in source.data
    assert "y" in source.data
    assert len(source.data["x"]) == 3
    assert len(source.data["y"]) == 3
    assert source.data["x"] == [1, 2, 3]
    assert source.data["y"] == [4, 5, 6]
    assert isinstance(source, ColumnDataSource)
