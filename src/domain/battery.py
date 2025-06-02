from domain.graph import Axis, AxisType, AxisRange, Graph
from typing import List

BATTERY_GRAPHS: List[Graph] = [
    Graph(
        x_axis=Axis(
            property="Discharge capacity",
            axis_type=AxisType.LINEAR,
            unit="mA*h/g",
            axis_range=AxisRange(min_value=0, max_value=2000)
        ),
        y_axis=Axis(
            property="Voltage",
            axis_type=AxisType.LINEAR,
            unit="V",
            axis_range=AxisRange(min_value=0, max_value=5)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Charge capacity",
            axis_type=AxisType.LINEAR,
            unit="mA*h/g",
            axis_range=AxisRange(min_value=0, max_value=2000)
        ),
        y_axis=Axis(
            property="Voltage",
            axis_type=AxisType.LINEAR,
            unit="V",
            axis_range=AxisRange(min_value=0, max_value=5)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Cycle number",
            axis_type=AxisType.LINEAR,
            unit="-",
            axis_range=AxisRange(min_value=1, max_value=2000)
        ),
        y_axis=Axis(
            property="Discharge capacity",
            axis_type=AxisType.LINEAR,
            unit="mA*h/g",
            axis_range=AxisRange(min_value=0, max_value=2000)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="C rate",
            axis_type=AxisType.LINEAR,
            unit="-",
            axis_range=AxisRange(min_value=0, max_value=5)
        ),
        y_axis=Axis(
            property="Discharge capacity",
            axis_type=AxisType.LINEAR,
            unit="mA*h/g",
            axis_range=AxisRange(min_value=0, max_value=2000)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Time",
            axis_type=AxisType.LINEAR,
            unit="s",
            axis_range=AxisRange(min_value=1, max_value=1000)
        ),
        y_axis=Axis(
            property="Voltage",
            axis_type=AxisType.LINEAR,
            unit="V",
            axis_range=AxisRange(min_value=-3, max_value=3)
        ),
        data=[]
    ),
    Graph(
        x_axis=Axis(
            property="Cycle number",
            axis_type=AxisType.LINEAR,
            unit="-",
            axis_range=AxisRange(min_value=1, max_value=2000)
        ),
        y_axis=Axis(
            property="Voltage",
            axis_type=AxisType.LINEAR,
            unit="V",
            axis_range=AxisRange(min_value=-3, max_value=3)
        ),
        data=[]
    ),
]
