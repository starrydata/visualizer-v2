import json, os
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, Range1d, CustomJS, AjaxDataSource, LabelSet
)
from bokeh.embed import components
from bokeh.resources import CDN
import requests

# --- 外部JSファイル読込関数 ---
def load_js(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# --- 外部HTMLテンプレート読込関数 ---
def load_html_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

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

# --- 設定リスト ---
date_after="2024-01-01"
date_before="2025-05-09"
limit = 50
config = [
    # 1. Seebeck coefficient
    {
        "json_path": "https://visualizer.starrydata.org/all_curves/json/Temperature-Seebeck%20coefficient.json",
        "highlight_path": (
            "https://www.starrydata2.org/paperlist/xy_data_api/"
            f"?date_after={date_after}"
            f"&date_before={date_before}"
            "&property_x=Temperature"
            "&property_y=Seebeck%20coefficient"
            f"&limit={limit}"
        ),
        "x_range": (-5, 1150),
        "y_range": (-0.0003, 0.0003),
        "y_scale": "linear",
    },
    # 2. Electrical conductivity
    {
        "json_path": "https://visualizer.starrydata.org/all_curves/json/Temperature-Electrical%20conductivity.json",
        "highlight_path": (
            "https://www.starrydata2.org/paperlist/xy_data_api/"
            f"?date_after={date_after}"
            f"&date_before={date_before}"
            "&property_x=Temperature"
            "&property_y=Electrical%20conductivity"
            f"&limit={limit}"
        ),
        "x_range": (-5, 1150),
        "y_range": (1e2, 1e6),     # S/m の例
        "y_scale": "log",
    },
    # 3. Electrical resistivity
    {
        "json_path": "https://visualizer.starrydata.org/all_curves/json/Temperature-Electrical%20resistivity.json",
        "highlight_path": (
            "https://www.starrydata2.org/paperlist/xy_data_api/"
            f"?date_after={date_after}"
            f"&date_before={date_before}"
            "&property_x=Temperature"
            "&property_y=Electrical%20resistivity"
            f"&limit={limit}"
        ),
        "x_range": (-5, 1150),
        "y_range": (1e-6, 1e-2),     # Ω·m の例
        "y_scale": "log",
    },
    # 4. Thermal conductivity
    {
        "json_path": "https://visualizer.starrydata.org/all_curves/json/Temperature-Thermal%20conductivity.json",
        "highlight_path": (
            "https://www.starrydata2.org/paperlist/xy_data_api/"
            f"?date_after={date_after}"
            f"&date_before={date_before}"
            "&property_x=Temperature"
            "&property_y=Thermal%20conductivity"
            f"&limit={limit}"
        ),
        "x_range": (-5, 1150),
        "y_range": (5e-1, 2e+1),
        "y_scale": "log",
    },
    # 5. Power factor
    {
        "json_path": "https://visualizer.starrydata.org/all_curves/json/Temperature-Power%20factor.json",
        "highlight_path": (
            "https://www.starrydata2.org/paperlist/xy_data_api/"
            f"?date_after={date_after}"
            f"&date_before={date_before}"
            "&property_x=Temperature"
            "&property_y=Power%20factor"
            f"&limit={limit}"
        ),
        "x_range": (-5, 1150),
        "y_range": (1e-4, 1e-2),     # W/mK² の例
        "y_scale": "log",
    },
    # 6. ZT
    {
        "json_path": "https://visualizer.starrydata.org/all_curves/json/Temperature-ZT.json",
        "highlight_path": (
            "https://www.starrydata2.org/paperlist/xy_data_api/"
            f"?date_after={date_after}"
            f"&date_before={date_before}"
            "&property_x=Temperature"
            "&property_y=ZT"
            f"&limit={limit}"
        ),
        "x_range": (-5, 1150),
        "y_range": (0, 1.5),        # 一般的な ZT の範囲
        "y_scale": "linear",
    },
]

# --- 外部JSファイルパス ---
scatter_adapter_path = os.path.join(os.path.dirname(__file__), "js/scatter_adapter.js")
line_adapter_path = os.path.join(os.path.dirname(__file__), "js/line_adapter.js")
label_adapter_path = os.path.join(os.path.dirname(__file__), "js/label_adapter.js")

scatter_adapter_code = load_js(scatter_adapter_path)
line_adapter_code = load_js(line_adapter_path)
label_adapter_code = load_js(label_adapter_path)

divs, scripts, titles = [], [], []
for idx, cfg in enumerate(config):
    base_src, content = make_source(cfg['json_path'])
    titles.append(f"{content['prop_y']}")

    # AJAX データソース作成（highlight 傾向）
    hl_url = cfg['highlight_path']
    scatter_adapter = CustomJS(code=scatter_adapter_code)
    scatter_src = AjaxDataSource(
        data_url=hl_url,
        polling_interval=60000,
        mode='replace',
        content_type='application/json',
        adapter=scatter_adapter,
        method='GET'
    )

    # ── 追加：系列ごとの線用 AjaxDataSource ──
    line_adapter = CustomJS(code=line_adapter_code)
    line_src = AjaxDataSource(
        data_url=hl_url,
        polling_interval=60000,
        mode='replace',
        content_type='application/json',
        adapter=line_adapter,
        method='GET'
    )

    # ラベル用データソース
    label_adapter = CustomJS(code=label_adapter_code)
    label_src = AjaxDataSource(
        data_url=hl_url,
        polling_interval=60000,
        mode='replace',
        content_type='application/json',
        adapter=label_adapter,
        method='GET'
    )

    # プロット設定
    p = figure(
        x_axis_type='linear', y_axis_type=cfg['y_scale'],
        x_range=Range1d(*cfg['x_range']), y_range=Range1d(*cfg['y_range']),
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

    # ベースデータ
    p.circle('x', 'y', source=base_src,
             fill_color='blue', fill_alpha=1,
             size=1, line_width=0, line_color="#3288bd")

    # ── 追加：系列ごとに線を描画 ──
    p.multi_line(
        xs='xs', ys='ys', source=line_src,
        line_color='white', line_alpha=1,
        # widths フィールドを線幅にマッピング
        line_width={'field': 'widths'}
    )

    # ハイライトデータ（α=1、size は JS アダプタで計算したカラムを参照）
    p.circle('x', 'y', source=scatter_src,
             fill_color='white', fill_alpha=1,
             line_color='blue', line_alpha=1,
             size='size', line_width='line_size')

    # ラベル
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
    divs.append(div)
    scripts.append(script)

# HTMLテンプレート読込
template_path = os.path.join(os.path.dirname(__file__), "templates/starrydata_slideshow_with_menu.html")
html_template = load_html_template(template_path)

header_height = 40
menu_items = ''.join([f'<li id="menu{idx}">{t}</li>' for idx, t in enumerate(titles)])
plots_html = ''.join([
    f'<div id="plot{idx}" class="plot-container">{divs[idx]}{scripts[idx]}</div>'
    for idx in range(len(divs))
])

# テンプレート置換
html = html_template \
    .replace("{{CDN}}", CDN.render()) \
    .replace("{{header_height}}", str(header_height)) \
    .replace("{{menu_items}}", menu_items) \
    .replace("{{plots_html}}", plots_html)

# ファイル出力
out = './dist/starrydata_slideshow_with_menu.html'
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Generated: {out}")
