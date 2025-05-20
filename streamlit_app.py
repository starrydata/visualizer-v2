import sys
import os
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from application.services import GraphGenerationService, load_js_code

import json
import os
import datetime
import requests

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
    date_from = st.sidebar.date_input("From Date")
    date_to = st.sidebar.date_input("To Date")

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

    selected_graph_config = next(
        (g for g in config_data.get("graphs", []) if g["prop_x"] == prop_x and g["prop_y"] == prop_y),
        {}
    )

    default_x_range = selected_graph_config.get("x_range", [None, None])
    default_y_range = selected_graph_config.get("y_range", [None, None])

    x_min = st.sidebar.number_input("X Axis Min", value=default_x_range[0] if default_x_range[0] is not None else 0.0, key=f"x_min_{prop_x}_{prop_y}")
    x_max = st.sidebar.number_input("X Axis Max", value=default_x_range[1] if default_x_range[1] is not None else 1.0, key=f"x_max_{prop_x}_{prop_y}")

    y_min = st.sidebar.number_input("Y Axis Min", value=default_y_range[0] if default_y_range[0] is not None else 0.0, key=f"y_min_{prop_x}_{prop_y}")
    y_max = st.sidebar.number_input("Y Axis Max", value=default_y_range[1] if default_y_range[1] is not None else 1.0, key=f"y_max_{prop_x}_{prop_y}")

    x_scale = st.sidebar.selectbox("X Axis Scale", ["linear", "log"], index=0)
    y_scale = st.sidebar.selectbox("Y Axis Scale", ["linear", "log"], index=0)

    date_from = date_from.isoformat() if date_from else None
    date_to = date_to.isoformat() if date_to else None

    for g in config_data.get("graphs", []):
        if g.get("prop_x") == prop_x and g.get("prop_y") == prop_y:
            g["x_range"] = [x_min, x_max]
            g["y_range"] = [y_min, y_max]
            break

    scatter_js, line_js, label_js = load_js_code()
    graph_service = GraphGenerationService(scatter_js, line_js, label_js)

    json_base_uri = os.environ.get("JSON_BASE_URI")
    highlight_base_uri = os.environ.get("HIGHLIGHT_BASE_URI")

    json_path = f"{json_base_uri}/{prop_x}-{prop_y}.json"
    response = requests.get(json_path)
    response.raise_for_status()
    json_data = response.json()
    unit_x = json_data.get("unit_x", "")
    unit_y = json_data.get("unit_y", "")

    highlight_path = f"{highlight_base_uri}/?property_x={prop_x}&property_y={prop_y}&unit_x={unit_x}&unit_y={unit_y}&date_from={date_from}&date_to={date_to}&limit={limit}"

    div, script, title, figure = graph_service.create_graph(
        json_path,
        highlight_path,
        y_scale,
        [x_min, x_max],
        [y_min, y_max],
        x_scale,
        material_type=material_type,
    )

    st.subheader(f"Graph: {title}")

    st.bokeh_chart(figure, use_container_width=True)


if __name__ == "__main__":
    main()
