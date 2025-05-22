from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from bokeh.models import ColumnDataSource, Range1d
from bokeh.plotting import figure

from domain.graph import Graph, GraphDataPoint

class GraphCreator(ABC):
    def _load_local_json(self, file_path: str) -> dict:
        import json
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_config_and_create_graph(self, data: dict, y_scale: str, x_range: List[float], y_range: List[float], x_scale: str, material_type: str) -> Tuple[Graph, str]:
        config_path = f"src/config.{material_type}.json"
        config = self._load_local_json(config_path)
        axis_display = config.get("axis_display", "y")

        data_points = []
        unit_x = data.get("unit_x", "")
        unit_y = data.get("unit_y", "")

        d = data["data"]
        for xs, ys, sid in zip(d["x"], d["y"], d["SID"]):
            num_sid = int(sid)
            for j in range(len(xs)):
                x_val = xs[j]
                y_val = ys[j]
                data_points.append(GraphDataPoint(x_val, y_val, num_sid))

        graph = Graph(
            prop_x=data.get("prop_x", ""),
            prop_y=data.get("prop_y", ""),
            unit_x=unit_x,
            unit_y=unit_y,
            data_points=data_points,
            y_scale=y_scale,
            x_range=x_range,
            y_range=y_range,
        )

        if not graph.validate():
            raise ValueError("Graph data validation failed")

        return graph, axis_display

    def _create_base_source(self, data_points: List[GraphDataPoint]) -> ColumnDataSource:
        return ColumnDataSource(data=dict(
            x=[dp.x for dp in data_points],
            y=[dp.y for dp in data_points],
            SID=[dp.sid for dp in data_points],
        ))

    def _create_figure_base(self, graph: Graph, y_scale: str, x_scale: str, x_range: List[float], y_range: List[float]) -> figure:
        p = figure(
            x_axis_type=x_scale,
            y_axis_type=y_scale,
            x_range=Range1d(*x_range),
            y_range=Range1d(*y_range),
            x_axis_label=f"{graph.prop_x} ({graph.unit_x})",
            y_axis_label=f"{graph.prop_y} ({graph.unit_y})",
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
        p.outline_line_color = None
        return p

    @abstractmethod
    def create_graph(self, *args, **kwargs) -> Tuple[str, str, str, Optional[object]]:
        pass


