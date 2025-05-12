import json, os
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, Range1d, CustomJS, AjaxDataSource, LabelSet
)
from bokeh.embed import components
from bokeh.resources import CDN
import requests


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
config = [
    {
        "json_path": "https://visualizer.starrydata.org/all_curves/json/Temperature-Seebeck%20coefficient.json",
        "highlight_path": (
            "https://www.starrydata2.org/paperlist/xy_data_api/"
            "?date_before=2025-05-09"
            "&date_after=2024-01-01"
            "&property_x=Temperature"
            "&property_y=Seebeck%20coefficient"
            "&limit=20"
        ),
        "x_range": (-5, 1400),
        "y_range": (-0.0005, 0.0005),
        "y_scale": "linear",
    },
    {
        "json_path": "https://visualizer.starrydata.org/all_curves/json/Temperature-Thermal%20conductivity.json",
        "highlight_path": (
            "https://www.starrydata2.org/paperlist/xy_data_api/"
            "?date_before=2025-05-09"
            "&date_after=2024-01-01"
            "&property_x=Temperature"
            "&property_y=Thermal%20conductivity"
            "&limit=20"
        ),
        "x_range": (-5, 1400),
        "y_range": (1e-1, 5e+1),
        "y_scale": "log",
    },
]

divs, scripts, titles = [], [], []
for idx, cfg in enumerate(config):
    base_src, content = make_source(cfg['json_path'])
    titles.append(f"{content['prop_y']}")

    # AJAX データソース作成（highlight 傾向）
    hl_url = cfg['highlight_path']
    scatter_adapter = CustomJS(code="""
        const d = cb_data.response.data;
        let xf = [], yf = [], sidf = [], sizef = [];
        const ts = [];
        for (let i = 0; i < d.x.length; i++) {
            const t = new Date(d.updated_at[i]).getTime();
            for (let j = 0; j < d.x[i].length; j++) {
                xf.push(d.x[i][j]);
                yf.push(d.y[i][j]);
                sidf.push(d.SID[i]);
                ts.push(t);
            }
        }
        const mi = Math.min(...ts), ma = Math.max(...ts);
        ts.forEach(t => sizef.push(ma > mi ? 2 + (t - mi)/(ma - mi)*6 : 2));
        return { x: xf, y: yf, SID: sidf, size: sizef };
    """)
    scatter_src = AjaxDataSource(
        data_url=hl_url,
        polling_interval=60000,
        mode='replace',
        content_type='application/json',
        adapter=scatter_adapter,
        method='GET'
    )

    # ラベル用データソース
    label_adapter = CustomJS(code="""
        const d = cb_data.response.data;
        let xe = [], ye = [], lab = [];
        for (let i = 0; i < d.x.length; i++) {
            const xs = d.x[i], ys = d.y[i];
            xe.push(xs.length ? xs[xs.length - 1] : null);
            ye.push(ys.length ? ys[ys.length - 1] : null);
            lab.push(`${d.SID[i]}-${d.figure_id[i]}-${d.sample_id[i]}`);
        }
        return { x_end: xe, y_end: ye, label: lab };
    """)
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
             fill_color='blue', fill_alpha=0.4,
             size=1, line_width=0, line_color="#3288bd")

    # ハイライトデータ（α=1、size は JS アダプタで計算したカラムを参照）
    p.circle('x', 'y', source=scatter_src,
             fill_color='white', fill_alpha=1,
             line_color='#3288bd', line_alpha=1,
             size='size', line_width=0.2)
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

# HTML 組み立て
header_height = 40
menu_items = ''.join([f'<li id="menu{idx}">{t}</li>' for idx, t in enumerate(titles)])
plots_html = ''.join([
    f'<div id="plot{idx}" class="plot-container">{divs[idx]}{scripts[idx]}</div>'
    for idx in range(len(divs))
])
html = f'''<!DOCTYPE html>
<html lang="ja">
<head><meta charset="utf-8"><title>Starrydata Slideshow</title>{CDN.render()}
<style>
  html, body {{margin:0; padding:0; height:100%;}}
  #menu {{position:fixed; top:0; left:0; width:100%; height:{header_height}px;
           background:black; color:white; z-index:10; font-size: 12px;}}
  #menu ul {{display:inline-flex; margin:0; padding:10px; list-style:none;}}
  #menu li {{margin-right:30px; cursor:pointer;}}
  #menu li.active {{position: relative;}}
  /* 右端に☑️を表示 */
    #menu li.active::after {{
      content: '☑️';
      position: absolute;
      right: -1.3em;       /* 右からの余白 */
      top: 50%;
      transform: translateY(-50%);
    }}
  #content {{position:absolute; top:{header_height}px; left:0; right:0; bottom:0;}}
  .plot-container {{position:absolute; top:0; left:0; right:0; bottom:0;
                   opacity:0; transition:opacity 1s;}}
</style></head>
<body>
  <div id="menu"><span>Y axis: </span><ul>{menu_items}</ul></div>
  <div id="content">{plots_html}</div>
  <script>
    const items = [...document.querySelectorAll('#menu li')];
    let current = 1;
    items.forEach((it, i) => it.addEventListener('click', () => switchPlot(i)));
    items[0].classList.add('active');
    function switchPlot(to) {{
      if (to === current) return;
      document.getElementById('plot' + current).style.opacity = 0;
      document.getElementById('plot' + to).style.opacity = 1;
      items[current].classList.remove('active'); items[to].classList.add('active');
      current = to;
    }}    
    switchPlot(0);
    setInterval(() => switchPlot((current+1) % items.length), 50000);
  </script>
</body>
</html>'''

# ファイル出力
out = './dist/starrydata_slideshow_with_menu.html'
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Generated: {out}")
