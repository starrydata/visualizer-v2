import os

from domain.graph import Graph, GraphDataPoint
from domain.slideshow import Slideshow

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
import requests
from bokeh.models import ColumnDataSource, Range1d, CustomJS, AjaxDataSource, LabelSet
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN

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
        p.xgrid.grid_line_color, p.xgrid.grid_line_alpha = "#ccc", 0.1
        p.ygrid.grid_line_color, p.ygrid.grid_line_alpha = "#ccc", 0.1
        p.outline_line_color = None
        return p

    @abstractmethod
    def create_graph(self, *args, **kwargs) -> Tuple[str, str, str, Optional[object]]:
        pass

class SlideshowGraphCreator(GraphCreator):
    def __init__(self):
        base_path = "src/static/js"
        with open(f"{base_path}/scatter_adapter.js", encoding="utf-8") as f:
            self.scatter_js = f.read().strip()
        with open(f"{base_path}/line_adapter.js", encoding="utf-8") as f:
            self.line_js = f.read().strip()


    def fetch_json(self, json_path: str) -> dict:
        resp = requests.get(json_path)
        resp.raise_for_status()
        return resp.json()

    def create_graph(self, json_path: str, highlight_path: str, y_scale: str, x_range: List[float], y_range: List[float], x_scale: str = "linear", material_type: str = "thermoelectric") -> Tuple[str, str, str, object]:
        content = self.fetch_json(json_path)
        graph, axis_display = self._load_config_and_create_graph(content, y_scale, x_range, y_range, x_scale, material_type)

        data_points = graph.data_points
        base_src = self._create_base_source(data_points)

        scatter_adapter = CustomJS(code=self.scatter_js)
        scatter_src = AjaxDataSource(
            data_url=highlight_path,
            polling_interval=60000,
            mode="replace",
            content_type="application/json",
            adapter=scatter_adapter,
            method="GET",
        )

        line_adapter = CustomJS(code=self.line_js)
        line_src = AjaxDataSource(
            data_url=highlight_path,
            polling_interval=60000,
            mode="replace",
            content_type="application/json",
            adapter=line_adapter,
            method="GET",
        )

        p = self._create_figure_base(graph, y_scale, x_scale, x_range, y_range)

        p.circle(
            "x",
            "y",
            source=base_src,
            fill_color="blue",
            fill_alpha=1,
            size=1,
            line_width=0,
            line_color="#3288bd",
        )

        p.multi_line(
            xs="xs",
            ys="ys",
            source=line_src,
            line_color="white",
            line_alpha=1,
            line_width={"field": "widths"},
        )

        p.circle(
            "x",
            "y",
            source=scatter_src,
            fill_color="white",
            fill_alpha=1,
            line_color="blue",
            line_alpha=1,
            size="size",
            line_width="line_size",
        )

        labels = LabelSet(
            x="x_end",
            y="y_end",
            text="label",
            source=line_src,
            x_offset=5,
            y_offset=5,
            text_font_size="8pt",
            text_color="white",
            background_fill_color="black",
            border_line_color="black",
            border_line_width=3,
        )
        p.add_layout(labels)

        div, script = components(p)
        if axis_display == "y":
            title = graph.prop_y
        else:
            title = f"{graph.prop_x} / {graph.prop_y}"
        return div, script, title, p

    def save_graph_html(self, div: str, script: str, prop_x: str, prop_y: str, output_dir: str = "./dist/graphs") -> str:
        safe_x_name = prop_x.replace(" ", "_")
        safe_y_name = prop_y.replace(" ", "_")
        single_out = f"{output_dir}/{safe_x_name}_{safe_y_name}.html"

        single_html = f"""
        <html>
        <head>{CDN.render()}</head>
        <body>
        {div}
        {script}
        </body>
        </html>
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        with open(single_out, "w", encoding="utf-8") as f:
            f.write(single_html)
        print(f"Generated single graph HTML: {single_out}")
        return single_out

class StreamlitGraphCreator(GraphCreator):
    def __init__(self):
        pass

    def create_graph(self, base_data: dict, highlight_points: dict, highlight_lines: dict, sizef_points: List[float], line_sizef_points: List[float], x_end: List[float], y_end: List[float], label: List[str], widths: List[float], y_scale: str, x_range: List[float], y_range: List[float], x_scale: str = "linear", material_type: str = "thermoelectric") -> Tuple[str, str, str, object]:
        graph, axis_display = self._load_config_and_create_graph(base_data, y_scale, x_range, y_range, x_scale, material_type)

        data_points = graph.data_points
        base_src = self._create_base_source(data_points)

        x_expanded_points = []
        y_expanded_points = []
        sid_expanded_points = []
        size_expanded_points = []
        line_size_expanded_points = []

        for i in range(len(highlight_points.get("x", []))):
            xs = highlight_points["x"][i]
            ys = highlight_points["y"][i]
            sid = highlight_points.get("SID", [])[i] if i < len(highlight_points.get("SID", [])) else ""
            size_val = sizef_points[i] if i < len(sizef_points) else 2
            line_size_val = line_sizef_points[i] if i < len(line_sizef_points) else 0.1
            for _ in xs:
                x_expanded_points.append(_)
                size_expanded_points.append(size_val)
                line_size_expanded_points.append(line_size_val)
            for y in ys:
                y_expanded_points.append(y)
            for _ in xs:
                sid_expanded_points.append(sid)

        highlight_points_src = ColumnDataSource(data=dict(
            x=x_expanded_points,
            y=y_expanded_points,
            SID=sid_expanded_points,
            size=size_expanded_points,
            line_size=line_size_expanded_points,
        ))

        highlight_lines_src = ColumnDataSource(data=dict(
            xs=highlight_lines.get("x", []),
            ys=highlight_lines.get("y", []),
            x_end=x_end,
            y_end=y_end,
            label=label,
            widths=widths,
        ))

        p = self._create_figure_base(graph, y_scale, x_scale, x_range, y_range)

        p.circle(
            "x",
            "y",
            source=base_src,
            fill_color="blue",
            fill_alpha=1,
            size=1,
            line_width=0,
            line_color="#3288bd",
        )

        p.multi_line(
            xs="xs",
            ys="ys",
            source=highlight_lines_src,
            line_color="white",
            line_alpha=1,
            line_width=0.5 #{"field": "widths"},
        )

        p.circle(
            "x",
            "y",
            source=highlight_points_src,
            fill_color="white",
            fill_alpha=1,
            line_color="blue",
            line_alpha=1,
            size=4, #"size",
            line_width=0.2 #"line_size",
        )

        # labels = LabelSet(
        #     x="x_end",
        #     y="y_end",
        #     text="label",
        #     source=highlight_lines_src,
        #     x_offset=5,
        #     y_offset=5,
        #     text_font_size="8pt",
        #     text_color="white",
        #     background_fill_color="black",
        #     border_line_color="black",
        #     border_line_width=3,
        # )
        # p.add_layout(labels)

        div, script = components(p)
        if axis_display == "y":
            title = graph.prop_y
        else:
            title = f"{graph.prop_x} / {graph.prop_y}"
        return div, script, title, p

    def save_graph_html(self, div: str, script: str, prop_x: str, prop_y: str, output_dir: str = "./dist/graphs") -> str:
        safe_x_name = prop_x.replace(" ", "_")
        safe_y_name = prop_y.replace(" ", "_")
        single_out = f"{output_dir}/{safe_x_name}_{safe_y_name}.html"

        single_html = f"""
        <html>
        <head>{CDN.render()}</head>
        <body>
        {div}
        {script}
        </body>
        </html>
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        with open(single_out, "w", encoding="utf-8") as f:
            f.write(single_html)
        print(f"Generated single graph HTML: {single_out}")
        return single_out
