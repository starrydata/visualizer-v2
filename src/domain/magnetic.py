from domain.graph import Axis, AxisType, AxisRange, Graph, XYPoint, XYPoints, XYSeries
from typing import List

# 参考：https://starrydata2.slack.com/archives/C02KSPC2S4U/p1749009336154709?thread_ts=1748851611.445249&cid=C02KSPC2S4U

empty_xy_points = XYPoints(
    data=[],
    updated_at="",
    sid="",
    figure_id="",
    sample_id="",
    composition=None
)

empty_xy_series = XYSeries(data=[empty_xy_points])

MAGNETIC_GRAPHS: List[Graph] = [
    Graph(
        x_axis=Axis(
            property="Magnetic field",
            axis_type=AxisType.LINEAR,
            unit="T",
            axis_range=AxisRange(min_value=-5.0, max_value=5.0)
        ),
        y_axis=Axis(
            property="Magnetization",
            axis_type=AxisType.LINEAR,
            unit="T",
            axis_range=AxisRange(min_value=-5.0, max_value=5.0)
        ),
        data=empty_xy_series
    ),
    Graph(
        x_axis=Axis(
            property="Magnetic field",
            axis_type=AxisType.LINEAR,
            unit="T",
            axis_range=AxisRange(min_value=-0.5, max_value=0.5)
        ),
        y_axis=Axis(
            property="magnetization_per_volume",
            axis_type=AxisType.LINEAR,
            unit="A/m",
            axis_range=AxisRange(min_value=-20.0, max_value=20.0)
        ),
        data=empty_xy_series
    ),
    Graph(
        x_axis=Axis(
            property="Magnetic field",
            axis_type=AxisType.LINEAR,
            unit="T",
            axis_range=AxisRange(min_value=-50.0, max_value=50.0)
        ),
        y_axis=Axis(
            property="magnetization_per_weight",
            axis_type=AxisType.LINEAR,
            unit="emu/g",
            axis_range=AxisRange(min_value=-300.0, max_value=300.0)
        ),
        data=empty_xy_series
    ),
    Graph(
        x_axis=Axis(
            property="Magnetic field strength (H)",
            axis_type=AxisType.LINEAR,
            unit="A/m",
            axis_range=AxisRange(min_value=-1500.0, max_value=1500.0)
        ),
        y_axis=Axis(
            property="Magnetization",
            axis_type=AxisType.LINEAR,
            unit="T",
            axis_range=AxisRange(min_value=-2.0, max_value=2.0)
        ),
        data=empty_xy_series
    ),
    Graph(
        x_axis=Axis(
            property="Magnetic field strength (H)",
            axis_type=AxisType.LINEAR,
            unit="A/m",
            axis_range=AxisRange(min_value=-20000.0, max_value=20000.0)
        ),
        y_axis=Axis(
            property="magnetization_per_volume",
            axis_type=AxisType.LINEAR,
            unit="A/m",
            axis_range=AxisRange(min_value=-1.0, max_value=1.0)
        ),
        data=empty_xy_series
    ),
    Graph(
        x_axis=Axis(
            property="Magnetic field strength (H)",
            axis_type=AxisType.LINEAR,
            unit="A/m",
            axis_range=AxisRange(min_value=-20000.0, max_value=20000.0)
        ),
        y_axis=Axis(
            property="magnetization_per_weight",
            axis_type=AxisType.LINEAR,
            unit="emu/g",
            axis_range=AxisRange(min_value=-50.0, max_value=50.0)
        ),
        data=empty_xy_series
    ),
    Graph(
        x_axis=Axis(
            property="Temperature",
            axis_type=AxisType.LINEAR,
            unit="K",
            axis_range=AxisRange(min_value=0.0, max_value=1000.0)
        ),
        y_axis=Axis(
            property="Magnetization",
            axis_type=AxisType.LINEAR,
            unit="T",
            axis_range=AxisRange(min_value=0.0, max_value=1.0)
        ),
        data=empty_xy_series
    ),

    Graph(
        x_axis=Axis(
            property="Temperature",
            axis_type=AxisType.LINEAR,
            unit="K",
            axis_range=AxisRange(min_value=0.0, max_value=1000.0)
        ),
        y_axis=Axis(
            property="magnetization_per_weight",
            axis_type=AxisType.LINEAR,
            unit="emu/g",
            axis_range=AxisRange(min_value=0.0, max_value=200.0)
        ),
        data=empty_xy_series
    ),
]
