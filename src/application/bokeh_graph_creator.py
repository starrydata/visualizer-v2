from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from bokeh.models import ColumnDataSource, Range1d
from bokeh.plotting import figure

from domain.graph import Graph
from itertools import chain

class BokehGraphCreator():
    def _load_local_json(self, file_path: str) -> dict:
        import json
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def create_bokeh_figure(self, graph: Graph) -> figure:
        p = figure(
            x_axis_type=graph.x_axis.axis_type.value,
            y_axis_type=graph.y_axis.axis_type.value,
            x_range=Range1d(graph.x_axis.axis_range.min_value, graph.x_axis.axis_range.max_value),
            y_range=Range1d(graph.y_axis.axis_range.min_value, graph.y_axis.axis_range.max_value),
            x_axis_label=f"{graph.x_axis.property} ({graph.x_axis.unit})",
            y_axis_label=f"{graph.y_axis.property} ({graph.y_axis.unit})",
        )

        # p = figure(
        #     x_axis_type=x_scale,
        #     y_axis_type=y_scale,
        #     x_range=Range1d(*x_range),
        #     y_range=Range1d(*y_range),
        #     x_axis_label=f"{graph.prop_x} ({graph.unit_x})",
        #     y_axis_label=f"{graph.prop_y} ({graph.unit_y})",
        #     background_fill_color="black",
        #     border_fill_color="black",
        #     sizing_mode="stretch_both",
        # )
        # for axis in (p.xaxis, p.yaxis):
        #     axis.axis_label_text_color = "#ccc"
        #     axis.major_label_text_color = "#ccc"
        #     axis.axis_label_text_font_style = "normal"
        # p.xgrid.grid_line_color, p.xgrid.grid_line_alpha = "#ccc", 0.1
        # p.ygrid.grid_line_color, p.ygrid.grid_line_alpha = "#ccc", 0.1
        # p.outline_line_color = None
        return p

    def create_bokeh_data_source(self, graph: Graph) -> ColumnDataSource:
        # 各データポイントをフラットなリストにまとめる
        all_points = list(chain.from_iterable(series.data for series in graph.data_point_series))
        data = {
            "x": [point.x for point in all_points],
            "y": [point.y for point in all_points],
            "SID": [""] * len(all_points),
        }
        return ColumnDataSource(data=data)


