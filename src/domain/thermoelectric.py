from domain.graph import Axis, AxisType, AxisRange, Graph
from typing import List

THERMOELECTRIC_GRAPHS: List[Graph] = [
    Graph(
        x_axis=Axis(
            property="Temperature",
            axis_type=AxisType.LINEAR,
            unit="K",
            axis_range=AxisRange(min_value=-5, max_value=1150)
        ),
        y_axis=Axis(
            property="Seebeck coefficient",
            axis_type=AxisType.LINEAR,
            unit="V/K",
            axis_range=AxisRange(min_value=-300, max_value=300)
        ),
        data_point_series=[]
    ),
    Graph(
        x_axis=Axis(
            property="Temperature",
            axis_type=AxisType.LINEAR,
            unit="K",
            axis_range=AxisRange(min_value=-5, max_value=1150)
        ),
        y_axis=Axis(
            property="Electrical conductivity",
            axis_type=AxisType.LOGARITHMIC,
            unit="S/m",
            axis_range=AxisRange(min_value=100, max_value=1000000)
        ),
        data_point_series=[]
    ),
    Graph(
        x_axis=Axis(
            property="Temperature",
            axis_type=AxisType.LINEAR,
            unit="K",
            axis_range=AxisRange(min_value=-5, max_value=1150)
        ),
        y_axis=Axis(
            property="Electrical resistivity",
            axis_type=AxisType.LOGARITHMIC,
            unit="Ω·m",
            axis_range=AxisRange(min_value=1e-6, max_value=1e+4)
        ),
        data_point_series=[]
    ),
    Graph(
        x_axis=Axis(
            property="Temperature",
            axis_type=AxisType.LINEAR,
            unit="K",
            axis_range=AxisRange(min_value=-5, max_value=1150)
        ),
        y_axis=Axis(
            property="Thermal conductivity",
            axis_type=AxisType.LINEAR,
            unit="W/(m·K)",
            axis_range=AxisRange(min_value=0, max_value=10)
        ),
        data_point_series=[]
    ),
    Graph(
        x_axis=Axis(
            property="Temperature",
            axis_type=AxisType.LINEAR,
            unit="K",
            axis_range=AxisRange(min_value=-5, max_value=1150)
        ),
        y_axis=Axis(
            property="Power factor",
            axis_type=AxisType.LINEAR,
            unit="W/(m·K²)",
            axis_range=AxisRange(min_value=0, max_value=0.01)
        ),
        data_point_series=[]
    ),
    Graph(
        x_axis=Axis(
            property="Temperature",
            axis_type=AxisType.LINEAR,
            unit="K",
            axis_range=AxisRange(min_value=-5, max_value=1150)
        ),
        y_axis=Axis(
            property="ZT",
            axis_type=AxisType.LINEAR,
            unit="-",
            axis_range=AxisRange(min_value=0, max_value=1.5)
        ),
        data_point_series=[]
    ),
]
