import sys
import os
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.main import generate_single_graph

def main():
    st.title("Nightmode Slideshow Graph Viewer")

    st.sidebar.header("API Parameters")

    # material type選択を追加
    material_type = st.sidebar.selectbox(
        "Select Material Type", ["thermoelectric", "battery"], index=1
    )

    limit = st.sidebar.number_input(
        "Limit", min_value=1, max_value=100, value=10, step=1
    )
    from_date = st.sidebar.date_input("From Date")
    to_date = st.sidebar.date_input("To Date")

    # material_typeに応じてconfigファイルを切り替え
    import json
    import os
    import datetime

    config_path = os.path.join(
        os.path.dirname(__file__), "src", f"config.{material_type}.json"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    graph_options = [(g["prop_x"], g["prop_y"]) for g in config_data.get("graphs", [])]

    selected_graph = st.sidebar.selectbox(
        "Select Graph", graph_options, index=0, format_func=lambda x: f"{x[0]} - {x[1]}", key="select_graph"
    )

    prop_x, prop_y = selected_graph

    # 選択されたグラフの設定を取得
    selected_graph_config = next(
        (g for g in config_data.get("graphs", []) if g["prop_x"] == prop_x and g["prop_y"] == prop_y),
        {}
    )

    # display unitのデフォルト値は空文字にする（jsonファイルから取得するため）
    default_unit_x = selected_graph_config.get("unit_x", "")
    default_unit_y = selected_graph_config.get("unit_y", "")

    # x_range, y_rangeのデフォルト値を取得
    default_x_range = selected_graph_config.get("x_range", [None, None])
    default_y_range = selected_graph_config.get("y_range", [None, None])

    # X軸用単位入力欄を追加（グラフごとに切り替え可能）
    unit_input_x = st.sidebar.text_input("Display Unit for X Axis (e.g. m, cm, inch)", value=default_unit_x, key=f"unit_x_{prop_x}_{prop_y}")

    # Y軸用単位入力欄を追加（グラフごとに切り替え可能）
    unit_input_y = st.sidebar.text_input("Display Unit for Y Axis (e.g. m, cm, inch)", value=default_unit_y, key=f"unit_y_{prop_x}_{prop_y}")

    # X軸のmin/max入力欄を追加（グラフごとに切り替え可能）
    x_min = st.sidebar.number_input("X Axis Min", value=default_x_range[0] if default_x_range[0] is not None else 0.0, key=f"x_min_{prop_x}_{prop_y}")
    x_max = st.sidebar.number_input("X Axis Max", value=default_x_range[1] if default_x_range[1] is not None else 1.0, key=f"x_max_{prop_x}_{prop_y}")

    # Y軸のmin/max入力欄を追加（グラフごとに切り替え可能）
    y_min = st.sidebar.number_input("Y Axis Min", value=default_y_range[0] if default_y_range[0] is not None else 0.0, key=f"y_min_{prop_x}_{prop_y}")
    y_max = st.sidebar.number_input("Y Axis Max", value=default_y_range[1] if default_y_range[1] is not None else 1.0, key=f"y_max_{prop_x}_{prop_y}")

    # material_typeに応じてconfigファイルを切り替え
    import json
    import os
    import datetime

    config_path = os.path.join(
        os.path.dirname(__file__), "src", f"config.{material_type}.json"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    graph_options = [(g["prop_x"], g["prop_y"]) for g in config_data.get("graphs", [])]

    selected_graph = st.sidebar.selectbox(
        "Select Graph", graph_options, index=0, format_func=lambda x: f"{x[0]} - {x[1]}"
    )

    prop_x, prop_y = selected_graph

    # X軸スケール選択追加
    x_scale = st.sidebar.selectbox("X Axis Scale", ["linear", "log"], index=0)
    # Y軸スケール選択追加
    y_scale = st.sidebar.selectbox("Y Axis Scale", ["linear", "log"], index=0)

    # 日付をtimestamp文字列に変換（例としてISOフォーマット）
    after = to_date.isoformat() if to_date else None
    before = from_date.isoformat() if from_date else None

    # x_range, y_rangeをmin/max入力欄の値でconfig_dataのgraphsに反映
    for g in config_data.get("graphs", []):
        if g.get("prop_x") == prop_x and g.get("prop_y") == prop_y:
            g["x_range"] = [x_min, x_max]
            g["y_range"] = [y_min, y_max]
            break

    div, script, title, figure = generate_single_graph(
        prop_x,
        prop_y,
        after=after,
        before=before,
        limit=limit,
        material_type=material_type,
        x_scale=x_scale,
        y_scale=y_scale,
        display_unit_x=unit_input_x,
        display_unit_y=unit_input_y,
    )

    st.subheader(f"Graph: {title}")

    # BokehのFigureオブジェクトをStreamlitで表示
    st.bokeh_chart(figure, use_container_width=True)


if __name__ == "__main__":
    main()
