import os
import streamlit as st
from streamlit_javascript import st_javascript
import datetime
import pytz
from presentation.bokeh_graph_creator import BokehGraphCreator
from streamlit_bokeh import streamlit_bokeh

from domain.material_type import MaterialType
from domain.graph import Axis, AxisRange, AxisType
from domain.graph_config_factory import get_graph_configs
from domain.graph import DateHighlightCondition

def main(material_type: MaterialType):
    st.title(f"{material_type.value.capitalize()} material data")

    date_from = st.sidebar.date_input("From Date")
    date_to = st.sidebar.date_input("To Date")

    # JavaScriptでブラウザのタイムゾーンを取得
    user_timezone_str = st_javascript("Intl.DateTimeFormat().resolvedOptions().timeZone", key="timezone")
    if not user_timezone_str:
        user_timezone_str = "UTC"  # 取得できなければUTCをデフォルトに

    user_timezone = pytz.timezone(user_timezone_str)

    if date_from:
        date_from_dt = datetime.datetime.combine(date_from, datetime.time(0, 0, 0))
        date_from_dt = user_timezone.localize(date_from_dt)

    if date_to:
        date_to_dt = datetime.datetime.combine(date_to, datetime.time(23, 59, 59))
        date_to_dt = user_timezone.localize(date_to_dt)

    # configファイルをPythonファイルから読み込む
    CONFIG_GRAPHS = get_graph_configs(material_type)

    graph_options = [(g.x_axis.property, g.y_axis.property) for g in CONFIG_GRAPHS]

    selected_graph = st.sidebar.selectbox(
        "Select Graph", graph_options, index=0, format_func=lambda x: f"{x[0]} - {x[1]}", key="select_graph"
    )

    prop_x, prop_y = selected_graph

    config = next(
        (g for g in CONFIG_GRAPHS if g.x_axis.property == prop_x and g.y_axis.property == prop_y)
    )
    x_axis = config.x_axis
    y_axis = config.y_axis

    x_min = st.sidebar.number_input("X Axis Min", value=x_axis.axis_range.min_value, key=f"x_min_{prop_x}_{prop_y}")
    x_max = st.sidebar.number_input("X Axis Max", value=x_axis.axis_range.max_value, key=f"x_max_{prop_x}_{prop_y}")
    y_min = st.sidebar.number_input("Y Axis Min", value=y_axis.axis_range.min_value, key=f"y_min_{prop_x}_{prop_y}")
    y_max = st.sidebar.number_input("Y Axis Max", value=y_axis.axis_range.max_value, key=f"y_max_{prop_x}_{prop_y}")

    x_type = st.sidebar.selectbox("X Axis Scale", ["linear", "log"], index=0 if x_axis.axis_type.value=="linear" else 1)
    y_type = st.sidebar.selectbox("Y Axis Scale", ["linear", "log"], index=0 if y_axis.axis_type.value=="linear" else 1)

    graph_creator = BokehGraphCreator()
    new_x_axis = Axis(
        property=prop_x,
        unit=x_axis.unit,
        axis_type=AxisType(x_type),
        axis_range=AxisRange(
            min_value=x_min,
            max_value=x_max
        )
    )
    new_y_axis = Axis(
        property=prop_y,
        unit=y_axis.unit,
        axis_type=AxisType(y_type),
        axis_range=AxisRange(
            min_value=y_min,
            max_value=y_max
        )
    )
    highlight_condition = None
    if date_from and date_to:
        highlight_condition = DateHighlightCondition(date_from=str(date_from), date_to=str(date_to))

    bokeh_figure = graph_creator.create_bokeh_figure(
        x_axis=new_x_axis,
        y_axis=new_y_axis,
        highlight_condition=highlight_condition
    )

    st.subheader(f"Graph: {prop_x} vs {prop_y}")



    streamlit_bokeh(bokeh_figure, use_container_width=True, theme="streamlit", key="my_unique_key")
