import json
import os
import requests
import urllib.parse
from application.slideshow_graph_creator_service import SlideshowGraphCreator
from application.slideshow_generation_service import SlideshowGenerationService
from domain.slideshow import Slideshow
from bokeh.resources import CDN

import sys



def main():
    STARRYDATA_BULK_DATA_API = os.environ.get("STARRYDATA_BULK_DATA_API")
    STARRYDATA2_API_XY_DATA = os.environ.get("STARRYDATA2_API_XY_DATA")

    # コマンドライン引数または環境変数で材料種別を指定（デフォルトは thermoelectric）
    material_type = None
    date_from_arg = None
    date_to_arg = None
    highlight_limit_arg = None
    if len(sys.argv) > 1:
        material_type = sys.argv[1].lower()
    if len(sys.argv) > 2:
        date_from_arg = sys.argv[2]
    if len(sys.argv) > 3:
        date_to_arg = sys.argv[3]
    if len(sys.argv) > 4:
        highlight_limit_arg = int(sys.argv[4])

    # 引数が足りていないエラーを出す
    if material_type is None:
        print("Usage: python presentation/slideshow_app.py <material_type> [date_from] [date_to] [highlight_limit]")
        sys.exit(1)


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
        print(f"Processing graph: {cfg['prop_x']} vs {cfg['prop_y']}")
        json_path = f"{STARRYDATA_BULK_DATA_API}/{cfg['prop_x']}-{cfg['prop_y']}.json"
        # JSONを取得してunit_x, unit_yを抽出
        response = requests.get(json_path)
        response.raise_for_status()
        base_data = response.json()
        unit_x = base_data.get("unit_x", "")
        unit_y = base_data.get("unit_y", "")

        params = {
            "property_x": cfg["prop_x"],
            "property_y": cfg["prop_y"],
            "unit_x": unit_x,
            "unit_y": unit_y,
            "date_from": date_from_arg if date_from_arg is not None else config_data["date_from"],
            "date_to": date_to_arg if date_to_arg is not None else config_data["date_to"],
            "limit": highlight_limit_arg if highlight_limit_arg is not None else config_data["limit"],
        }
        query_string = urllib.parse.urlencode(params)
        highlight_path = f"{STARRYDATA2_API_XY_DATA}/?{query_string}"

        div, script, title, figure = graph_service.create_bokeh_graph(
            json_path, highlight_path, cfg["y_scale"], cfg["x_range"], cfg["y_range"], cfg.get("x_scale", "linear"), material_type=material_type
        )
        graphs.add_graph(div, script, title)

        # グラフHTMLファイルの生成をサービスに移行
        # single_out = graph_service.save_graph_html(div, script, cfg["prop_x"], cfg["prop_y"])

    material_type = config_data.get("material_type", material_type)

    out_path, html_content = slideshow_service.generate_slideshow(
        graphs,
        material_type=material_type,
        date_from=date_from_arg if date_from_arg is not None else config_data["date_from"],
        date_to=date_to_arg if date_to_arg is not None else config_data["date_to"],
    )
    print(f"Generated slideshow at: {out_path}")

if __name__ == "__main__":
    main()
