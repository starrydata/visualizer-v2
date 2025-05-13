import json
import os
from graph_generator import generate_graph, generate_slideshow
from bokeh.resources import CDN

def main():
    # 環境変数からURIを取得
    json_base_uri = os.environ.get("JSON_BASE_URI", "")
    highlight_base_uri = os.environ.get("HIGHLIGHT_BASE_URI", "")

    with open("src/config.json", "r", encoding="utf-8") as f:
        config_data = json.load(f)

    graphs = []
    for idx, cfg in enumerate(config_data["config"]):
        # json_pathとhighlight_pathを環境変数のベースURIと組み合わせて作成
        json_path = f"{json_base_uri}/{cfg['prop_x']}-{cfg['prop_y']}.json"
        highlight_path = f"{highlight_base_uri}/?property_x={cfg['prop_x']}&property_y={cfg['prop_y']}&date_after=2024-01-01&date_before=2025-05-09&limit=50"

        div, script, title = generate_graph(
            json_path, highlight_path, cfg["y_scale"], cfg["x_range"], cfg["y_range"]
        )
        graphs.append((div, script, title))

        # ファイル名をX軸とY軸の名前をベースに作成
        safe_x_name = cfg["prop_x"].replace(" ", "_")
        safe_y_name = cfg["prop_y"].replace(" ", "_")
        single_out = f"./dist/graphs/graph_{safe_x_name}_{safe_y_name}.html"

        # 単体グラフのHTMLをdist/graphsに生成
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

    out_path, html_content = generate_slideshow(graphs)
    print(f"Generated slideshow at: {out_path}")

if __name__ == "__main__":
    main()
