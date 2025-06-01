import pytest
from domain.graph import Axis, AxisType, AxisRange, XYPoint, XYPoints, XYSeries, Graph, DateHighlightCondition


def test_axis_range():
    r = AxisRange(min_value=0, max_value=10)
    assert r.min_value == 0
    assert r.max_value == 10


def test_axis():
    axis = Axis(property="Voltage", axis_type=AxisType.LINEAR, unit="V", axis_range=AxisRange(0, 5))
    assert axis.property == "Voltage"
    assert axis.axis_type == AxisType.LINEAR
    assert axis.unit == "V"
    assert axis.axis_range.min_value == 0
    assert axis.axis_range.max_value == 5


def test_data_point():
    p = XYPoint(x=1.0, y=2.0)
    assert p.x == 1.0
    assert p.y == 2.0


def test_data_points():
    points = [XYPoint(1, 2), XYPoint(3, 4)]
    dp = XYPoints(points, updated_at="2024-01-01T00:00:00Z")
    assert len(dp.data) == 2
    assert dp.data[0].x == 1
    assert dp.data[1].y == 4
    assert dp.updated_at == "2024-01-01T00:00:00Z"


def test_xy_series():
    points1 = XYPoints([XYPoint(1, 2)], updated_at="2024-01-01T00:00:00Z")
    points2 = XYPoints([XYPoint(3, 4)], updated_at="2024-01-01T00:00:00Z")
    series = XYSeries([points1, points2])
    assert len(series.data) == 2
    assert series.data[0].data[0].x == 1
    assert series.data[1].data[0].y == 4
    assert series.data[0].updated_at == "2024-01-01T00:00:00Z"


def test_graph():
    x_axis = Axis(property="x", axis_type=AxisType.LINEAR, unit="", axis_range=AxisRange(0, 1))
    y_axis = Axis(property="y", axis_type=AxisType.LOGARITHMIC, unit="", axis_range=AxisRange(0, 10))
    data_points = [XYPoints([XYPoint(1, 2)], updated_at="2024-01-01T00:00:00Z")]
    series = XYSeries(data_points)
    graph = Graph(x_axis=x_axis, y_axis=y_axis, data=series)
    assert graph.x_axis.property == "x"
    assert graph.y_axis.axis_type == AxisType.LOGARITHMIC
    assert len(graph.data.data) == 1
    assert graph.data.data[0].data[0].y == 2
    assert graph.data.data[0].updated_at == "2024-01-01T00:00:00Z"


def test_date_highlight_condition_in_range():
    cond = DateHighlightCondition(date_from="2024-01-01", date_to="2024-01-31")
    points = XYPoints([XYPoint(x=1.0, y=2.0)], updated_at="2024-01-15T12:00:00Z")
    assert cond.is_match_points(points)


def test_date_highlight_condition_out_of_range():
    cond = DateHighlightCondition(date_from="2024-01-01", date_to="2024-01-31")
    points = XYPoints([XYPoint(x=1.0, y=2.0)], updated_at="2024-02-01T00:00:00Z")
    assert not cond.is_match_points(points)


def test_date_highlight_condition_on_boundary():
    cond = DateHighlightCondition(date_from="2024-01-01", date_to="2024-01-31")
    points_from = XYPoints([XYPoint(x=1.0, y=2.0)], updated_at="2024-01-01T00:00:00Z")
    points_to = XYPoints([XYPoint(x=1.0, y=2.0)], updated_at="2024-01-31T23:59:59Z")
    assert cond.is_match_points(points_from)
    assert cond.is_match_points(points_to)
