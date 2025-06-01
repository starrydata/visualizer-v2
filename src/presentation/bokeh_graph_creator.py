from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, Range1d

from application.graph_data_service import GraphDataService, XYPointsListDTO, XYPointsDTO
from domain.graph import Graph, Axis, AxisType, AxisRange

class BokehGraphCreator():
    def __init__(self, graph_data_service: GraphDataService = GraphDataService()):
        self.graph_data_service = graph_data_service

    def get_data_point_series_with_axis(self, prop_x: str, prop_y: str, unit_x: str = "", unit_y: str = "") -> XYPointsListDTO:
        merged_data_dto = self.graph_data_service.get_merged_graph_data(prop_x, prop_y, unit_x, unit_y)
        return merged_data_dto

    def to_bokeh_axis_type(self, axis_type: AxisType) -> str:
        if axis_type == AxisType.LINEAR:
            return "linear"
        elif axis_type == AxisType.LOGARITHMIC:
            return "log"
        return "linear" # デフォルトはlinear

    def create_bokeh_figure(self, x_axis: Axis, y_axis: Axis, highlight_condition=None):
        p = figure(
            title=f"{x_axis.property} vs {y_axis.property}",
            x_axis_type=x_axis.axis_type.value,
            y_axis_type=y_axis.axis_type.value,
            x_range=Range1d(x_axis.axis_range.min_value, x_axis.axis_range.max_value),
            y_range=Range1d(y_axis.axis_range.min_value, y_axis.axis_range.max_value),
            x_axis_label=f"{x_axis.property} ({x_axis.unit})",
            y_axis_label=f"{y_axis.property} ({y_axis.unit})",
        )

        # highlight_conditionがあれば渡す
        if highlight_condition is not None:
            xy_points_list_dto = self.graph_data_service.get_merged_graph_data(
                x_axis.property, y_axis.property, x_axis.unit, y_axis.unit, highlight_condition=highlight_condition
            )
        else:
            xy_points_list_dto = self.get_data_point_series_with_axis(x_axis.property, y_axis.property, x_axis.unit, y_axis.unit)
        column_data_source = self.create_bokeh_data_source(xy_points_list_dto)
        renderer = p.scatter(
            "x",
            "y",
            source=column_data_source,
            fill_alpha=1,
            size=2,
            line_width=0,
            color="color",  # 色分けのためにcolor列を指定
        )
        hover = HoverTool(tooltips=[("SID", "@SID")], renderers=[renderer], mode="mouse", point_policy="follow_mouse")
        p.add_tools(hover)
        return p

    def create_bokeh_data_source(self, xy_points_list_dto: XYPointsListDTO) -> ColumnDataSource:
        from itertools import chain
        # XYPointsDTOごとにis_highlightedを展開
        all_points = []
        color = []
        for dto in xy_points_list_dto.data:
            all_points.extend(dto.data)
            color.extend(["red" if dto.is_highlighted else "gray"] * len(dto.data))
        data = dict(
            x=[point.x for point in all_points],
            y=[point.y for point in all_points],
            SID=["" for _ in all_points],
            color=color,
        )
        return ColumnDataSource(data=data)

