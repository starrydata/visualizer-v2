import json
import os
from application.services import GraphGenerationService, SlideshowGenerationService, load_js_code
from domain.slideshow import Slideshow
from bokeh.resources import CDN

def main():
    json_base_uri = os.environ.get("JSON_BASE_URI", "")
    highlight_base_uri = os.environ.get("HIGHLIGHT_BASE_URI", "")

    with open("src/config.json", "r", encoding="utf-8") as f:
        config_data = json.load(f)

    scatter_js, line_js, label_js = load_js_code()
    graph_service = GraphGenerationService(scatter_js, line_js, label_js)
    slideshow_service = SlideshowGenerationService()

    graphs = Slideshow([])

    for cfg in config_data["config"]:
        json_path = f"{json_base_uri}/{cfg['prop_x']}-{cfg['prop_y']}.json"
        highlight_path = f"{highlight_base_uri}/?property_x={cfg['prop_x']}&property_y={cfg['prop_y']}&date_after=2024-01-01&date_before=2025-05-09&limit=50"

        div, script, title = graph_service.create_graph(
            json_path, highlight_path, cfg["y_scale"], cfg["x_range"], cfg["y_range"]
        )
        graphs.add_graph(div, script, title)

        safe_x_name = cfg["prop_x"].replace(" ", "_")
        safe_y_name = cfg["prop_y"].replace(" ", "_")
        single_out = f"./dist/graphs/graph_{safe_x_name}_{safe_y_name}.html"

        single_html = f"""
        <html>
        <head>{CDN.render()}</head>
        <body>
        {div}
        {script}
        </body>
        </html>
        """
        os.makedirs(os.path.dirname(single_out), exist_ok=True)
        with open(single_out, "w", encoding="utf-8") as f:
            f.write(single_html)
        print(f"Generated single graph HTML: {single_out}")

    out_path, html_content = slideshow_service.generate_slideshow(graphs)
    print(f"Generated slideshow at: {out_path}")

if __name__ == "__main__":
    main()
