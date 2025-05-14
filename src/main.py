import json
import os
from application.services import GraphGenerationService, SlideshowGenerationService, load_js_code
from domain.slideshow import Slideshow
from bokeh.resources import CDN

def main():
    json_base_uri = os.environ.get("JSON_BASE_URI", "")
    highlight_base_uri = os.environ.get("HIGHLIGHT_BASE_URI", "")

    with open("src/config.thermoelectric.json", "r", encoding="utf-8") as f:
        config_data = json.load(f)

    scatter_js, line_js, label_js = load_js_code()
    graph_service = GraphGenerationService(scatter_js, line_js, label_js)
    slideshow_service = SlideshowGenerationService()

    graphs = Slideshow([])

    for cfg in config_data["graphs"]:
        json_path = f"{json_base_uri}/{cfg['prop_x']}-{cfg['prop_y']}.json"
        highlight_path = f"{highlight_base_uri}/?property_x={cfg['prop_x']}&property_y={cfg['prop_y']}&date_after=2024-01-01&date_before=2025-05-09&limit=50"

        div, script, title = graph_service.create_graph(
            json_path, highlight_path, cfg["y_scale"], cfg["x_range"], cfg["y_range"]
        )
        graphs.add_graph(div, script, title)

        # グラフHTMLファイルの生成をサービスに移行
        single_out = graph_service.save_graph_html(div, script, cfg["prop_x"], cfg["prop_y"])

    # material_typeをconfig.jsonの内容から取得
    material_type = config_data.get("material_type", "starrydata")

    out_path, html_content = slideshow_service.generate_slideshow(graphs, material_type=material_type)
    print(f"Generated slideshow at: {out_path}")

if __name__ == "__main__":
    main()
