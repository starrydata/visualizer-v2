from src.domain.graph import XYPoint, XYPoints, XYSeries, Graph, Axis, AxisType, AxisRange

def make_xy_point(x=0.0, y=0.0):
    return XYPoint(x=x, y=y)

def make_xy_points(
    data=None,
    updated_at="2024-01-01T00:00:00Z",
    sid="test-sid",
    figure_id="fig-1",
    sample_id="sample-1",
    composition="comp-1"
):
    if data is None:
        data = [make_xy_point()]
    return XYPoints(
        data=data,
        updated_at=updated_at,
        sid=sid,
        figure_id=figure_id,
        sample_id=sample_id,
        composition=composition
    )

def make_xy_series(points_list=None):
    if points_list is None:
        points_list = [make_xy_points()]
    return XYSeries(data=points_list)

def make_axis(property="x", axis_type=AxisType.LINEAR, unit="V", axis_range=None):
    if axis_range is None:
        axis_range = AxisRange(min_value=0, max_value=1)
    return Axis(property=property, axis_type=axis_type, unit=unit, axis_range=axis_range)

def make_graph():
    return Graph(
        x_axis=make_axis("x"),
        y_axis=make_axis("y"),
        data=make_xy_series()
    )
