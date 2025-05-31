from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, Range1d

from application.graph_data_service import GraphDataService
from domain.graph import DataPointsSeries, Graph, Axis, AxisType, AxisRange

class BokehGraphCreator():
    def __init__(self, graph_data_service: GraphDataService):
        self.graph_data_service = graph_data_service

    def get_data_point_series_with_axis(self, prop_x: str, prop_y: str, unit_x: str = "", unit_y: str = "") -> DataPointsSeries:
        merged_data_series = self.graph_data_service.get_merged_graph_data(prop_x, prop_y, unit_x, unit_y)
        return merged_data_series

    def to_bokeh_axis_type(self, axis_type: AxisType) -> str:
        if axis_type == AxisType.LINEAR:
            return "linear"
        elif axis_type == AxisType.LOGARITHMIC:
            return "log"
        return "linear" # デフォルトはlinear

    def create_bokeh_figure(self, x_axis: Axis, y_axis: Axis):
        p = figure(
            x_axis_type=x_axis.axis_type.value,
            y_axis_type=y_axis.axis_type.value,
            x_range=Range1d(x_axis.axis_range.min_value, x_axis.axis_range.max_value),
            y_range=Range1d(y_axis.axis_range.min_value, y_axis.axis_range.max_value),
            x_axis_label=f"{x_axis.property} ({x_axis.unit})",
            y_axis_label=f"{y_axis.property} ({y_axis.unit})",
            background_fill_color="black",
            border_fill_color="black",
            sizing_mode="stretch_both",
        )

        for axis in (p.xaxis, p.yaxis):
            axis.axis_label_text_color = "#ccc"
            axis.major_label_text_color = "#ccc"
            axis.axis_label_text_font_style = "normal"
        p.xgrid.grid_line_color, p.xgrid.grid_line_alpha = "#ccc", 0.1
        p.ygrid.grid_line_color, p.ygrid.grid_line_alpha = "#ccc", 0.1

        data_points_series = self.get_data_point_series_with_axis(x_axis.property, y_axis.property, x_axis.unit, y_axis.unit)
        column_data_source = self.create_bokeh_data_source(data_points_series)
        renderer = p.circle(
            "x",
            "y",
            source=column_data_source,
            fill_alpha=1,
            # size=2,
            line_width=0,
        )
        hover = HoverTool(tooltips=[("SID", "@SID")], renderers=[renderer], mode="mouse", point_policy="follow_mouse")
        p.add_tools(hover)

        return p

    def create_bokeh_data_source(self, data_points_series) -> ColumnDataSource:
        from itertools import chain
        # Graph型もDataPointsSeries型も受け付ける
        if hasattr(data_points_series, 'data_point_series'):
            # Graph型
            all_points = list(chain.from_iterable(series.data for series in data_points_series.data_point_series))
        elif hasattr(data_points_series, 'data'):
            # DataPointsSeries型
            all_points = list(chain.from_iterable(series.data for series in data_points_series.data))
        else:
            raise ValueError('Invalid data_points_series type')
        data = {
            "x": [point.x for point in all_points],
            "y": [point.y for point in all_points],
            "SID": ["" for _ in all_points],
        }
        return ColumnDataSource(data=data)

