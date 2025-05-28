import os
from typing import List, Tuple

import requests
from bokeh.embed import components
from bokeh.models import CustomJS, AjaxDataSource, LabelSet
from bokeh.resources import CDN

from application.graph_creator_service import GraphCreator


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

        xy_data = graph.xy_data
        base_src = self._create_base_source(xy_data)

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
            fill_color="#9BB0FF",
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
            text_alpha={"field": "alphas"},
            background_fill_color="black",
            background_fill_alpha={"field": "alphas"},
            border_line_color="black",
            border_line_width=3,
            border_line_alpha={"field": "alphas"},
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
        # APP_ENVがstagingの場合は、output_dirを/dist/stating/graphsに変更
        if os.getenv("APP_ENV") == "local":
            output_dir = "./dist/local/graphs"
        # directoryがない場合は作成
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
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
        os.makedirs(output_dir, exist_ok=True)
        with open(single_out, "w", encoding="utf-8") as f:
            f.write(single_html)
        print(f"Generated single graph HTML: {single_out}")
        return single_out
