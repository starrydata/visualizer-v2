import pytest
from bokeh.plotting import figure
from domain.graph import Axis, AxisType, AxisRange, XYPoint, XYPoints, DateHighlightCondition
from presentation.bokeh_graph_creator import BokehGraphCreator
from application.graph_data_service import GraphDataService, XYPointsDTO, XYSeriesDTO
from unittest.mock import MagicMock
from src.tests.domain.graph_mock_factory import make_xy_points

@pytest.fixture
def mock_graph_data_service():
    service = MagicMock(spec=GraphDataService)
    return service

@pytest.fixture
def bokeh_graph_creator(mock_graph_data_service):
    return BokehGraphCreator(graph_data_service=mock_graph_data_service)

@pytest.fixture
def axes():
    x_axis = Axis(property="x", axis_type=AxisType.LINEAR, unit="", axis_range=AxisRange(0, 10))
    y_axis = Axis(property="y", axis_type=AxisType.LINEAR, unit="", axis_range=AxisRange(0, 10))
    return x_axis, y_axis

def test_create_bokeh_figure_basic(bokeh_graph_creator, mock_graph_data_service, axes):
    x_axis, y_axis = axes
    # モックデータ（DTO方式）
    points = make_xy_points([XYPoint(1, 2), XYPoint(3, 4)], updated_at="2024-01-01T00:00:00Z", sid="test-sid", figure_id="fig-1", sample_id="sample-1", composition="comp-1")
    dto = XYPointsDTO(data=points.data, is_highlighted=False, sid=points.sid, figure_id=points.figure_id, sample_id=points.sample_id, composition=points.composition)
    dto_list = XYSeriesDTO(data=[dto])
    mock_graph_data_service.get_merged_graph_data.return_value = dto_list
    fig = bokeh_graph_creator.create_bokeh_figure(x_axis, y_axis)
    assert isinstance(fig, figure)
    # x/y range, axis label
    from bokeh.models import Range1d
    assert isinstance(fig.x_range, Range1d)
    assert isinstance(fig.y_range, Range1d)
    assert fig.x_range.start == 0
    assert fig.x_range.end == 10
    assert fig.y_range.start == 0
    assert fig.y_range.end == 10
    assert fig.xaxis[0].axis_label == "x ()"
    assert fig.yaxis[0].axis_label == "y ()"

def test_create_bokeh_figure_with_highlight(bokeh_graph_creator, mock_graph_data_service, axes):
    x_axis, y_axis = axes
    # ハイライト条件
    highlight_condition = DateHighlightCondition(date_from="2024-01-01", date_to="2024-01-02")
    # モックデータ（DTO方式）
    points1 = make_xy_points([XYPoint(1, 2)], updated_at="2024-01-01T00:00:00Z", sid="test-sid", figure_id="fig-1", sample_id="sample-1", composition="comp-1")  # ハイライト
    points2 = make_xy_points([XYPoint(3, 4)], updated_at="2024-01-02T00:00:00Z", figure_id="fig-2", sample_id="sample-2", composition="comp-2")  # 非ハイライト
    points3 = make_xy_points([XYPoint(5, 6)], updated_at="2024-01-03T00:00:00Z", figure_id="fig-3", sample_id="sample-3", composition="comp-3")
    dto1 = XYPointsDTO(data=points1.data, is_highlighted=True, sid=points1.sid, figure_id=points1.figure_id, sample_id=points1.sample_id, composition=points1.composition)
    dto2 = XYPointsDTO(data=points2.data, is_highlighted=False, sid=points2.sid, figure_id=points2.figure_id, sample_id=points2.sample_id, composition=points2.composition)
    dto3 = XYPointsDTO(data=points3.data, is_highlighted=False, sid=points3.sid, figure_id=points3.figure_id, sample_id=points3.sample_id, composition=points3.composition)
    dto_list = XYSeriesDTO(data=[dto1, dto2, dto3])
    mock_graph_data_service.get_merged_graph_data.return_value = dto_list
    fig = bokeh_graph_creator.create_bokeh_figure(x_axis, y_axis, highlight_condition=highlight_condition)
    assert isinstance(fig, figure)
    # get_merged_graph_dataが正しく呼ばれているか
    mock_graph_data_service.get_merged_graph_data.assert_called_with(
        x_axis.property, y_axis.property, x_axis.unit, y_axis.unit, highlight_condition=highlight_condition
    )
