from typing import List, Tuple

from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.resources import CDN

from application.graph_creator_service import GraphCreator


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

        base_renderer = p.circle(
            "x",
            "y",
            source=base_src,
            fill_color="blue",
            fill_alpha=1,
            size=2,
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

        highlight_renderer = p.circle(
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

        from bokeh.models import HoverTool
        base_hover = HoverTool(tooltips=[("SID", "@SID")], renderers=[base_renderer, highlight_renderer], mode="mouse", point_policy="follow_mouse")
        p.add_tools(base_hover)

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
