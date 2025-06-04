from domain.graph import Axis, AxisType, AxisRange, Graph
from typing import List

# 参考：https://starrydata2.slack.com/archives/C02KSPC2S4U/p1749009336154709?thread_ts=1748851611.445249&cid=C02KSPC2S4U

MAGNETIC_GRAPHS: List[Graph] = [
    Graph(
        x_axis=Axis(
            property="Magnetic field",
            axis_type=AxisType.LINEAR,
            unit="T",

            axis_range=AxisRange(min_value=0.0, max_value=1.5)
        ),
        y_axis=Axis(
            property="Magnetization",
            axis_type=AxisType.LINEAR,
            unit="T",
            axis_range=AxisRange(min_value=-1.0, max_value=1.0)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Magnetic field",
            axis_type=AxisType.LINEAR,
            unit="T",
            axis_range=AxisRange(min_value=0.0, max_value=1.5)
        ),
        y_axis=Axis(
            property="magnetization_per_volume",
            axis_type=AxisType.LINEAR,
            unit="A/m",
            axis_range=AxisRange(min_value=-1000.0, max_value=1000.0)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Magnetic field",
            axis_type=AxisType.LINEAR,
            unit="T",
            axis_range=AxisRange(min_value=0.0, max_value=1.5)
        ),
        y_axis=Axis(
            property="magnetization_per_weight",
            axis_type=AxisType.LINEAR,
            unit="emu/g",
            axis_range=AxisRange(min_value=-10.0, max_value=10.0)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Magnetic field strength (H)",
            axis_type=AxisType.LINEAR,
            unit="A/m",
            axis_range=AxisRange(min_value=0.0, max_value=1200.0)
        ),
        y_axis=Axis(
            property="Magnetization",
            axis_type=AxisType.LINEAR,
            unit="T",
            axis_range=AxisRange(min_value=-1.0, max_value=1.0)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Magnetic field strength (H)",
            axis_type=AxisType.LINEAR,
            unit="A/m",
            axis_range=AxisRange(min_value=0.0, max_value=1200.0)
        ),
        y_axis=Axis(
            property="magnetization_per_volume",
            axis_type=AxisType.LINEAR,
            unit="A/m",
            axis_range=AxisRange(min_value=-1000.0, max_value=1000.0)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Magnetic field strength (H)",
            axis_type=AxisType.LINEAR,
            unit="A/m",
            axis_range=AxisRange(min_value=0.0, max_value=1200.0)
        ),
        y_axis=Axis(
            property="magnetization_per_weight",
            axis_type=AxisType.LINEAR,
            unit="emu/g",
            axis_range=AxisRange(min_value=-10.0, max_value=10.0)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Temperature",
            axis_type=AxisType.LINEAR,
            unit="K",
            axis_range=AxisRange(min_value=0.0, max_value=400.0)
        ),
        y_axis=Axis(
            property="Magnetization",
            axis_type=AxisType.LINEAR,
            unit="T",
            axis_range=AxisRange(min_value=-1.0, max_value=1.0)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Temperature",
            axis_type=AxisType.LINEAR,
            unit="K",
            axis_range=AxisRange(min_value=0.0, max_value=400.0)
        ),
        y_axis=Axis(
            property="magnetization_per_volume",
            axis_type=AxisType.LINEAR,
            unit="A/m",
            axis_range=AxisRange(min_value=-1000.0, max_value=1000.0)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Temperature",
            axis_type=AxisType.LINEAR,
            unit="K",
            axis_range=AxisRange(min_value=0.0, max_value=400.0)
        ),
        y_axis=Axis(
            property="magnetization_per_weight",
            axis_type=AxisType.LINEAR,
            unit="emu/g",
            axis_range=AxisRange(min_value=-10.0, max_value=10.0)
        ),
        data=[]
    ),
]
