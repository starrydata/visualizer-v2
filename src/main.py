import json
import os
from application.services import GraphGenerationService, SlideshowGenerationService, load_js_code
from domain.slideshow import Slideshow
from bokeh.resources import CDN

import sys

def generate_single_graph(prop_x, prop_y, after=None, before=None, limit=None, material_type=None):
    json_base_uri = os.environ.get("JSON_BASE_URI", "")
    highlight_base_uri = os.environ.get("HIGHLIGHT_BASE_URI", "")

    if material_type is None:
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

    # 引数で渡された場合はconfig_dataの値を上書き
    if after is not None:
        config_data['before'] = after
    if before is not None:
        config_data['after'] = before
    if limit is not None:
        config_data['limit'] = limit

    # prop_x, prop_yに一致するグラフ設定を探す
    graph_cfg = None
    for g in config_data.get("graphs", []):
        if g.get("prop_x") == prop_x and g.get("prop_y") == prop_y:
            graph_cfg = g
            break

    if graph_cfg is None:
        raise ValueError(f"Graph configuration not found for prop_x={prop_x}, prop_y={prop_y}")

    scatter_js, line_js, label_js = load_js_code()
    graph_service = GraphGenerationService(scatter_js, line_js, label_js)

    json_path = f"{json_base_uri}/{prop_x}-{prop_y}.json"
    highlight_path = f"{highlight_base_uri}/?property_x={prop_x}&property_y={prop_y}&date_after={config_data['after']}&date_before={config_data['before']}&limit={config_data['limit']}"

    # create_bokeh_figureメソッドを呼び出すように修正
    div, script, title, figure = graph_service.create_graph(
        json_path,
        highlight_path,
        graph_cfg.get("y_scale"),
        graph_cfg.get("x_range"),
        graph_cfg.get("y_range"),
        graph_cfg.get("x_scale", "linear"),
        material_type=material_type
    )

    return div, script, title, figure

def main(after=None, before=None, limit=None):
    json_base_uri = os.environ.get("JSON_BASE_URI", "")
    highlight_base_uri = os.environ.get("HIGHLIGHT_BASE_URI", "")

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

    scatter_js, line_js, label_js = load_js_code()
    graph_service = GraphGenerationService(scatter_js, line_js, label_js)
    slideshow_service = SlideshowGenerationService()

    graphs = Slideshow([])

    for cfg in config_data["graphs"]:
        json_path = f"{json_base_uri}/{cfg['prop_x']}-{cfg['prop_y']}.json"

        highlight_path = f"{highlight_base_uri}/?property_x={cfg['prop_x']}&property_y={cfg['prop_y']}&date_after={config_data['after']}&date_before={config_data['before']}&limit={config_data['limit']}"

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
