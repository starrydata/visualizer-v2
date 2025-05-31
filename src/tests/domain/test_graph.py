import pytest
from src.domain.graph import Axis, AxisType, AxisRange, DataPoint, DataPoints, DataPointsSeries, Graph


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
    p = DataPoint(x=1.0, y=2.0)
    assert p.x == 1.0
    assert p.y == 2.0


def test_data_points():
    points = [DataPoint(1, 2), DataPoint(3, 4)]
    dp = DataPoints(points)
    assert len(dp.data) == 2
    assert dp.data[0].x == 1
    assert dp.data[1].y == 4


def test_data_points_series():
    points1 = DataPoints([DataPoint(1, 2)])
    points2 = DataPoints([DataPoint(3, 4)])
    series = DataPointsSeries([points1, points2])
    assert len(series.data) == 2
    assert series.data[0].data[0].x == 1
    assert series.data[1].data[0].y == 4


def test_graph():
    x_axis = Axis(property="x", axis_type=AxisType.LINEAR, unit="", axis_range=AxisRange(0, 1))
    y_axis = Axis(property="y", axis_type=AxisType.LOGARITHMIC, unit="", axis_range=AxisRange(0, 10))
    data_points = [DataPoints([DataPoint(1, 2)])]
    graph = Graph(x_axis=x_axis, y_axis=y_axis, data_point_series=data_points)
    assert graph.x_axis.property == "x"
    assert graph.y_axis.axis_type == AxisType.LOGARITHMIC
    assert len(graph.data_point_series) == 1
    assert graph.data_point_series[0].data[0].y == 2
