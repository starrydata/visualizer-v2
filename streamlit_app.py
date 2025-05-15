import sys
import os
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import sys
import os
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.main import generate_single_graph
import streamlit.components.v1 as components

def main():
    st.title("Nightmode Slideshow Graph Viewer")

    st.sidebar.header("API Parameters")
    limit = st.sidebar.number_input("Limit", min_value=1, max_value=100, value=10, step=1)
    from_ = st.sidebar.text_input("From (timestamp or ID)", "")
    to = st.sidebar.text_input("To (timestamp or ID)", "")

    # グラフ選択用のリストをconfigファイルから取得
    import json
    import os
    config_path = os.path.join(os.path.dirname(__file__), "src", "config.thermoelectric.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    graph_options = [(g["prop_x"], g["prop_y"]) for g in config_data.get("graphs", [])]

    selected_graph = st.sidebar.selectbox("Select Graph", graph_options, format_func=lambda x: f"{x[0]} - {x[1]}")

    prop_x, prop_y = selected_graph

    div, script, title, figure = generate_single_graph(
        prop_x, prop_y,
        after=to if to != "" else None,
        before=from_ if from_ != "" else None,
        limit=limit
    )

    st.subheader(f"Graph: {title}")

    # BokehのFigureオブジェクトをStreamlitで表示
    st.bokeh_chart(figure, use_container_width=True)

    # 生成HTMLの大画面表示リンクを表示
    import os
    from src.main import main as generate_slideshow_html

    out_path = generate_slideshow_html(after=to if to != "" else None,
                                      before=from_ if from_ != "" else None,
                                      limit=limit)

    if out_path and os.path.exists(out_path):
        st.markdown(f"[Open generated slideshow in new tab]({out_path})", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
