import os
from typing import List, Tuple
import requests
from bokeh.models import ColumnDataSource, Range1d, CustomJS, AjaxDataSource, LabelSet
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN

from domain.graph import Graph, GraphDataPoint
from domain.slideshow import Slideshow

class GraphGenerationService:
    def __init__(self, scatter_js: str, line_js: str, label_js: str):
        self.scatter_js = scatter_js
        self.line_js = line_js
        self.label_js = label_js

    def fetch_json(self, json_path: str) -> dict:
        resp = requests.get(json_path)
        resp.raise_for_status()
        return resp.json()

    def load_local_json(self, file_path: str) -> dict:
        import json
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def create_graph(self, json_path: str, highlight_path: str, y_scale: str, x_range: List[float], y_range: List[float], x_scale: str = "linear", material_type: str = "thermoelectric") -> Tuple[str, str, str]:
        content = self.fetch_json(json_path)
        d = content["data"]

        # configファイル読み込み
        config_path = f"src/config.{material_type}.json"
        config = self.load_local_json(config_path)
        axis_display = config.get("axis_display", "y")

        data_points = []
        for xs, ys, sid in zip(d["x"], d["y"], d["SID"]):
            num_sid = int(sid)
            for j in range(len(xs)):
                data_points.append(GraphDataPoint(xs[j], ys[j], num_sid))

        graph = Graph(
            prop_x=content["prop_x"],
            prop_y=content["prop_y"],
            unit_x=content["unit_x"],
            unit_y=content["unit_y"],
            data_points=data_points,
            y_scale=y_scale,
            x_range=x_range,
            y_range=y_range,
        )

        if not graph.validate():
            raise ValueError("Graph data validation failed")

        base_src = ColumnDataSource(data=dict(
            x=[dp.x for dp in data_points],
            y=[dp.y for dp in data_points],
            SID=[dp.sid for dp in data_points],
        ))

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

class SlideshowGenerationService:
    def __init__(self, template_path: str = "src/templates/starrydata_slideshow.html"):
        self.template_path = template_path

    def generate_slideshow(self, graphs: Slideshow, material_type: str = "starrydata") -> Tuple[str, str]:
        divs = [div for div, _, _ in graphs.graphs]
        scripts = [script for _, script, _ in graphs.graphs]
        titles = graphs.get_titles()

        menu_items = "".join(
            [f'<li id="menu{idx}">{title}</li>' for idx, title in enumerate(titles)]
        )

        plots_html = "".join(
            [
                f'<div id="plot{idx}" class="plot-container">{divs[idx]}{scripts[idx]}</div>'
                for idx in range(len(divs))
            ]
        )

        with open(self.template_path, "r", encoding="utf-8") as f:
            template = f.read()

        html = (
            template.replace("{{ menu_items|safe }}", menu_items)
            .replace("{{ plots_html|safe }}", plots_html)
            .replace("{{ bokeh_cdn }}", CDN.render())
        )

        safe_material_type = material_type.replace(" ", "_").lower()
        out = f"./dist/{safe_material_type}_slideshow.html"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated: {out}")
        return out, html

def load_js_code():
    base_path = "src/static/js"
    with open(f"{base_path}/scatter_adapter.js", encoding="utf-8") as f:
        scatter_code = f.read().strip()
    with open(f"{base_path}/line_adapter.js", encoding="utf-8") as f:
        line_code = f.read().strip()
    with open(f"{base_path}/label_adapter.js", encoding="utf-8") as f:
        label_code = f.read().strip()
    return scatter_code, line_code, label_code
