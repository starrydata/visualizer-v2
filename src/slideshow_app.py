import json
import os
import requests
from application.graph_creator_service import SlideshowGraphCreator
from application.slideshow_generation_service import SlideshowGenerationService
from domain.slideshow import Slideshow
from bokeh.resources import CDN

import sys



def main(date_from=None, date_to=None, limit=None):
    BASE_DATA_URI = os.environ.get("BASE_DATA_URI")
    HIGHLIGHT_DATA_URI = os.environ.get("HIGHLIGHT_DATA_URI")

    # コマンドライン引数または環境変数で材料種別を指定（デフォルトは thermoelectric）
    material_type = None
    if len(sys.argv) > 1:
        material_type = sys.argv[1].lower()
    else:
        material_type = os.environ.get("MATERIAL_TYPE", "thermoelectric").lower()

    config_file_map = {
        "thermoelectric": "src/config.thermoelectric.json",
        "battery": "src/config.battery.json",
    }

    config_file = config_file_map.get(material_type)
    if not config_file:
        print(f"Unknown material type '{material_type}', defaulting to thermoelectric")
        config_file = config_file_map["thermoelectric"]

    with open(config_file, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    graph_service = SlideshowGraphCreator()
    slideshow_service = SlideshowGenerationService()

    graphs = Slideshow([])

    for cfg in config_data["graphs"]:
        json_path = f"{BASE_DATA_URI}/{cfg['prop_x']}-{cfg['prop_y']}.json"
        # JSONを取得してunit_x, unit_yを抽出
        response = requests.get(json_path)
        response.raise_for_status()
        base_data = response.json()
        unit_x = base_data.get("unit_x", "")
        unit_y = base_data.get("unit_y", "")

        highlight_path = f"{HIGHLIGHT_DATA_URI}/?property_x={cfg['prop_x']}&property_y={cfg['prop_y']}&unit_x={unit_x}&unit_y={unit_y}&date_from={config_data['date_from']}&date_to={config_data['date_to']}&limit={config_data['limit']}"

        div, script, title, figure = graph_service.create_graph(
            json_path, highlight_path, cfg["y_scale"], cfg["x_range"], cfg["y_range"], cfg.get("x_scale", "linear"), material_type=material_type
        )
        graphs.add_graph(div, script, title)

        # グラフHTMLファイルの生成をサービスに移行
        single_out = graph_service.save_graph_html(div, script, cfg["prop_x"], cfg["prop_y"])

    material_type = config_data.get("material_type", material_type)

    out_path, html_content = slideshow_service.generate_slideshow(graphs, material_type=material_type)
    print(f"Generated slideshow at: {out_path}")

if __name__ == "__main__":
    main()
