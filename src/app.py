import json, os
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, Range1d, CustomJS, AjaxDataSource, LabelSet
)
from bokeh.embed import components
from bokeh. resources import CDN
import requests


# --- 共通関数：JSON から ColumnDataSource を作る ---
def make_source(json_path):
    # URL かローカルファイルかで分岐
    if json_path.startswith(("http://", "https://")):
        # リモート JSON を GET
        resp = requests.get(json_path)
        resp.raise_for_status()
        content = resp.json()
    else:
        # ローカルファイルを読み込み
        with open(json_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

    # 以降はこれまでと同じ
    d = content['data']
    x_flat, y_flat = [], []
    for xs, ys in zip(d['x'], d['y']):
        x_flat += xs
        y_flat += ys
    return ColumnDataSource(data=dict(x=x_flat, y=y_flat)), content

# --- ここでまとめて管理する config 定義 ---
config = [
    {
        # ベースデータ（プロパティ名を変えれば該当JSONが取得可能）
        "json_path": "https://visualizer.starrydata.org/all_curves/json/Temperature-Seebeck%20coefficient.json",
        # xy_data_api の URL (最新20件を取得)
        "highlight_path": (
            "https://www.starrydata2.org/paperlist/xy_data_api/"
            "?date_before=2025-05-09"
            "&date_after=2025-01-01"
            "&property_x=Temperature"
            "&property_y=Seebeck%20coefficient"
            "&limit=20"
        ),
        "x_range": (1, 1400),
        "y_range": (1e-7, 1e-2),
    },
    {
        "json_path": "https://visualizer.starrydata.org/all_curves/json/Temperature-Thermal%20conductivity.json",
        "highlight_path": (
            "https://www.starrydata2.org/paperlist/xy_data_api/"
            "?date_before=2025-05-09"
            "&date_after=2025-01-01"
            "&property_x=Temperature"
            "&property_y=Thermal%20conductivity"
            "&limit=20"
        ),
        "x_range": (1, 1400),
        "y_range": (1e-1, 1e+3),
    },
    # 他のプロパティ組合せも同様に追加できます
]
divs, scripts = [], []

for cfg in config:
    # 1) ベースデータ読み込み
    base_src, content = make_source(cfg["json_path"])

    # 2) このグラフ固有の範囲を取得
    x_min, x_max = cfg["x_range"]
    y_min, y_max = cfg["y_range"]

    # 3) ハイライト用 JSON URL
    hl_url = cfg["highlight_path"]

    # 4) ハイライト用 AjaxDataSource／LabelSource を毎回新規生成
    flatten_adapter = CustomJS(code="""
        const resp = cb_data.response;
        const d = resp.data;
        const x_flat=[], y_flat=[], SID_flat=[], sample_flat=[], curator_flat=[];
        for(let i=0; i<d.x.length; i++){
            const xs=d.x[i], ys=d.y[i], cur=d.curator[i];
            for(let j=0; j<xs.length; j++){
                x_flat.push(xs[j]);
                y_flat.push(ys[j]);
                SID_flat.push(d.SID[i]);
                sample_flat.push(d.sample_id[i]);
                curator_flat.push(cur);
            }
        }
        return {
          x: x_flat, y: y_flat,
          SID: SID_flat, sample_id: sample_flat,
          curator: curator_flat
        };
    """)
    scatter_src = AjaxDataSource(
        data_url=hl_url,
        polling_interval=60000,
        mode='replace',
        content_type='application/json',
        adapter=flatten_adapter,
        method="GET"
    )

    label_adapter = CustomJS(code="""
        const resp = cb_data.response;
        const d = resp.data;
        const x_end=[], y_end=[], curator=[];
        for(let i=0; i<d.x.length; i++){
            const xs=d.x[i], ys=d.y[i];
            x_end.push(xs.length>0 ? xs[xs.length-1] : null);
            y_end.push(ys.length>0 ? ys[ys.length-1] : null);
            curator.push(d.curator[i]);
        }
        return { x_end: x_end, y_end: y_end, curator: curator };
    """)
    label_src = AjaxDataSource(
        data_url=hl_url,
        polling_interval=60000,
        mode='replace',
        content_type='application/json',
        adapter=label_adapter,
        method="GET"
    )

    # 5) プロット作成
    x_label = f"{content['prop_x']} ({content['unit_x']})"
    y_label = f"{content['prop_y']} ({content['unit_y']})"
    p = figure(
        x_axis_type="log",
        y_axis_type="log",
        x_range=Range1d(x_min, x_max),
        y_range=Range1d(y_min, y_max),
        x_axis_label=x_label,
        y_axis_label=y_label,
        background_fill_color="black",
        border_fill_color="black",
        sizing_mode="stretch_both"
    )

    # 軸ラベル／グリッド色の調整（省略できます）
    for axis in (p.xaxis, p.yaxis):
        axis.axis_label_text_color = "white"
        axis.major_label_text_color = "white"
    p.xgrid.grid_line_color, p.xgrid.grid_line_alpha = 'white', 0.1
    p.ygrid.grid_line_color, p.ygrid.grid_line_alpha = 'white', 0.1
    p.outline_line_color = None

    # ベースラインデータ
    p.scatter('x', 'y', source=base_src,
              fill_color='white', fill_alpha=0.9, line_color=None, size=1)

    # ハイライト
    p.scatter('x', 'y', source=scatter_src,
              fill_color='white', fill_alpha=1,
              line_color='blue', line_alpha=1.0,
              size=5, line_width=1)

    # ラベル
    labels = LabelSet(
        x='x_end', y='y_end', text='curator',
        source=label_src,
        x_offset=5, y_offset=5,
        text_font_size='8pt',
        text_color='white',
        render_mode='canvas'
    )
    p.add_layout(labels)

    # 6) components を取得
    div, script = components(p)
    divs.append(div)
    scripts.append(script)

# ⇒ あとは以前の HTML 組み立て部分に divs／scripts をはめ込んでください


# HTML 生成
html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>Starrydata Animated with Highlight</title>
  {CDN.render()}
  <style>
    html, body {{ width:100%; height:100%; margin:0; padding:0; }}
    .plot-container {{ position:absolute; top:0; left:0; width:100%; height:100%; transition: opacity 2s; }}
    #plot0 {{ opacity:1; z-index:2; }}
    #plot1 {{ opacity:0; z-index:1; }}
  </style>
</head>
<body>
  <div id="plot0" class="plot-container">
    {divs[0]}
    {scripts[0]}
  </div>
  <div id="plot1" class="plot-container">
    {divs[1]}
    {scripts[1]}
  </div>
  <script>
    let current = 0;
    setInterval(() => {{
      const next = 1 - current;
      const curEl = document.getElementById('plot' + current);
      const nxtEl = document.getElementById('plot' + next);
      curEl.style.opacity = 0;
      nxtEl.style.opacity = 1;
      curEl.style.zIndex = 1;
      nxtEl.style.zIndex = 2;
      current = next;
    }}, 10000);
  </script>
</body>
</html>
"""

# 書き出し
out_path = './dist/starrydata_animated_with_highlight.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Generated: {out_path}")
