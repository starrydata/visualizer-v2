import json, os
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, Range1d, CustomJS, AjaxDataSource, LabelSet
)
from bokeh.embed import components
from bokeh.resources import CDN
import requests

# --- CustomJSコードを外部ファイルから読み込む ---
with open("src/static/js/scatter_adapter.js", encoding="utf-8") as f:
    scatter_code = f.read().strip()
with open("src/static/js/line_adapter.js", encoding="utf-8") as f:
    line_code = f.read().strip()
with open("src/static/js/label_adapter.js", encoding="utf-8") as f:
    label_code = f.read().strip()


# --- 共通関数：JSON から ColumnDataSource を作る ---
def make_source(json_path):
    resp = requests.get(json_path)
    resp.raise_for_status()
    content = resp.json()

    d = content['data']
    x_flat, y_flat, sid_flat = [], [], []
    for xs, ys, sid in zip(d['x'], d['y'], d['SID']):
        num_sid = int(sid)
        for j in range(len(xs)):
            x_flat.append(xs[j])
            y_flat.append(ys[j])
            sid_flat.append(num_sid)

    return ColumnDataSource(data=dict(x=x_flat, y=y_flat, SID=sid_flat)), content


def generate_graph(json_path, highlight_path, y_scale, x_range, y_range):
    base_src, content = make_source(json_path)

    scatter_adapter = CustomJS(code=scatter_code)
    scatter_src = AjaxDataSource(
        data_url=highlight_path,
        polling_interval=60000,
        mode='replace',
        content_type='application/json',
        adapter=scatter_adapter,
        method='GET'
    )

    line_adapter = CustomJS(code=line_code)
    line_src = AjaxDataSource(
        data_url=highlight_path,
        polling_interval=60000,
        mode='replace',
        content_type='application/json',
        adapter=line_adapter,
        method='GET'
    )

    label_adapter = CustomJS(code=label_code)
    label_src = AjaxDataSource(
        data_url=highlight_path,
        polling_interval=60000,
        mode='replace',
        content_type='application/json',
        adapter=label_adapter,
        method='GET'
    )

    p = figure(
        x_axis_type='linear', y_axis_type=y_scale,
        x_range=Range1d(*x_range), y_range=Range1d(*y_range),
        x_axis_label=f"{content['prop_x']} ({content['unit_x']})",
        y_axis_label=f"{content['prop_y']} ({content['unit_y']})",
        background_fill_color='black', border_fill_color='black', sizing_mode='stretch_both'
    )
    for axis in (p.xaxis, p.yaxis):
        axis.axis_label_text_color = "#ccc"
        axis.major_label_text_color = "#ccc"
    p.xgrid.grid_line_color, p.xgrid.grid_line_alpha = '#ccc', 0.1
    p.ygrid.grid_line_color, p.ygrid.grid_line_alpha = '#ccc', 0.1
    p.outline_line_color = None

    p.circle('x', 'y', source=base_src,
             fill_color='blue', fill_alpha=1,
             size=1, line_width=0, line_color="#3288bd")

    p.multi_line(
        xs='xs', ys='ys', source=line_src,
        line_color='white', line_alpha=1,
        line_width={'field': 'widths'}
    )

    p.circle('x', 'y', source=scatter_src,
             fill_color='white', fill_alpha=1,
             line_color='blue', line_alpha=1,
             size='size', line_width='line_size')

    labels = LabelSet(
        x='x_end', y='y_end', text='label',
        source=label_src,
        x_offset=5, y_offset=5,
        text_font_size='8pt',
        text_color='white',
        background_fill_color='black',
        border_line_color='black',
        border_line_width=3
    )
    p.add_layout(labels)

    div, script = components(p)
    title = content['prop_y']
    return div, script, title


def generate_slideshow(graphs):
    divs, scripts, titles = [], [], []
    for div, script, title in graphs:
        divs.append(div)
        scripts.append(script)
        titles.append(title)

    header_height = 40
    menu_items = ''.join([f'<li id="menu{idx}">{t}</li>' for idx, t in enumerate(titles)])
    plots_html = ''.join([
        f'<div id="plot{idx}" class="plot-container">{divs[idx]}{scripts[idx]}</div>'
        for idx in range(len(divs))
    ])

    with open("src/templates/starrydata_slideshow.html", encoding="utf-8") as f:
        template = f.read()
    html = template.replace("{{ menu_items|safe }}", menu_items).replace("{{ plots_html|safe }}", plots_html).replace("{{ bokeh_cdn }}", CDN.render())
    out = './dist/starrydata_slideshow_with_menu.html'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated: {out}")
    return out, html


def main():
    import json
    import os

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
            json_path,
            highlight_path,
            cfg["y_scale"],
            cfg["x_range"],
            cfg["y_range"]
        )
        graphs.append((div, script, title))

        # ファイル名をX軸とY軸の名前をベースに作成
        safe_x_name = cfg['prop_x'].replace(" ", "_")
        safe_y_name = cfg['prop_y'].replace(" ", "_")
        single_out = f'./dist/graphs/graph_{safe_x_name}_{safe_y_name}.html'

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
        with open(single_out, 'w', encoding='utf-8') as f:
            f.write(single_html)
        print(f"Generated single graph HTML: {single_out}")

    out_path, html_content = generate_slideshow(graphs)
    print(f"Generated slideshow at: {out_path}")


if __name__ == "__main__":
    main()
