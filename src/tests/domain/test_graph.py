import pytest
from domain.graph import Axis, AxisType, AxisRange, XYPoint, XYPoints, XYSeries, Graph, DateHighlightCondition, SIDHighlightCondition
from src.tests.domain.graph_mock_factory import make_xy_points


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
    dp = make_xy_points(points, figure_id="fig-1", sample_id="sample-1", composition="comp-1")
    assert len(dp.data) == 2
    assert dp.data[0].x == 1
    assert dp.data[1].y == 4
    assert dp.updated_at == "2024-01-01T00:00:00Z"
    assert dp.figure_id == "fig-1"
    assert dp.sample_id == "sample-1"
    assert dp.composition == "comp-1"


def test_xy_series():
    points1 = make_xy_points([XYPoint(1, 2)], figure_id="fig-1", sample_id="sample-1", composition="comp-1")
    points2 = make_xy_points([XYPoint(3, 4)], figure_id="fig-2", sample_id="sample-2", composition="comp-2")
    series = XYSeries([points1, points2])
    assert len(series.data) == 2
    assert series.data[0].data[0].x == 1
    assert series.data[1].data[0].y == 4
    assert series.data[0].updated_at == "2024-01-01T00:00:00Z"
    assert series.data[0].figure_id == "fig-1"
    assert series.data[1].figure_id == "fig-2"


def test_graph():
    x_axis = Axis(property="x", axis_type=AxisType.LINEAR, unit="", axis_range=AxisRange(0, 1))
    y_axis = Axis(property="y", axis_type=AxisType.LOGARITHMIC, unit="", axis_range=AxisRange(0, 10))
    data_points = [make_xy_points([XYPoint(1, 2)])]
    series = XYSeries(data_points)
    graph = Graph(x_axis=x_axis, y_axis=y_axis, data=series)
    assert graph.x_axis.property == "x"
    assert graph.y_axis.axis_type == AxisType.LOGARITHMIC
    assert len(graph.data.data) == 1
    assert graph.data.data[0].data[0].y == 2
    assert graph.data.data[0].updated_at == "2024-01-01T00:00:00Z"

def test_date_highlight_condition_in_range():
    cond = DateHighlightCondition(date_from="2024-01-01", date_to="2024-01-31")
    points = make_xy_points([XYPoint(x=1.0, y=2.0)], updated_at="2024-01-15T12:00:00Z")
    assert cond.is_match_points(points)


def test_date_highlight_condition_out_of_range():
    cond = DateHighlightCondition(date_from="2024-01-01", date_to="2024-01-31")
    points = make_xy_points([XYPoint(x=1.0, y=2.0)], updated_at="2024-02-01T00:00:00Z")
    assert not cond.is_match_points(points)


def test_date_highlight_condition_on_boundary():
    cond = DateHighlightCondition(date_from="2024-01-01", date_to="2024-01-31")
    points_from = make_xy_points([XYPoint(x=1.0, y=2.0)], updated_at="2024-01-01T00:00:00Z")
    points_to = make_xy_points([XYPoint(x=1.0, y=2.0)], updated_at="2024-01-31T23:59:59Z")
    assert cond.is_match_points(points_from)
    assert cond.is_match_points(points_to)

def test_date_highlight_condition_microseconds():
    points = XYPoints(
        data=[
            XYPoint(x=1.01057, y=240.082),
        ],
        updated_at='2025-06-02T04:50:51.331000',
        sid='49993',
        figure_id='57222',
        sample_id='86360',
        composition=None
    )
    cond = DateHighlightCondition(date_from="2025-06-02T00:00:00+0900", date_to="2025-06-02T23:59:59+0900")
    assert cond.is_match_points(points) == True


def test_xy_points_with_sid():
    points = make_xy_points(
        [XYPoint(x=1.0, y=2.0)],
        updated_at="2024-01-15T12:00:00Z",
        sid="sidA"
    )
    assert points.sid == "sidA"


def test_sid_highlight_condition_match():
    cond = SIDHighlightCondition(sid="sid123")
    points = make_xy_points(
        [XYPoint(x=1.0, y=2.0)],
        updated_at="2024-01-15T12:00:00Z",
        sid="sid123"
    )
    assert cond.is_match_points(points)


def test_sid_highlight_condition_not_match():
    cond = SIDHighlightCondition(sid="sid999")
    points = make_xy_points(
        [XYPoint(x=1.0, y=2.0)],
        updated_at="2024-02-01T00:00:00Z",
        sid="sidB"
    )
    assert not cond.is_match_points(points)


def test_filter_by_sid():
    points1 = make_xy_points([XYPoint(1, 2)], updated_at="2024-01-01T00:00:00Z", sid="sidA")
    points2 = make_xy_points([XYPoint(3, 4)], updated_at="2024-01-02T00:00:00Z", sid="sidB")
    points3 = make_xy_points([XYPoint(5, 6)], updated_at="2024-01-03T00:00:00Z", sid="sidA")
    series = XYSeries([points1, points2, points3])
    filtered = [p for p in series.data if p.sid == "sidA"]
    assert len(filtered) == 2
    assert all(p.sid == "sidA" for p in filtered)
