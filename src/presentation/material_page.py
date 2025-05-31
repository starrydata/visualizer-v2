import os
import streamlit as st
from streamlit_javascript import st_javascript
from application.streamlit_graph_creator_service import StreamlitGraphCreator
from application.graph_data_service import GraphDataService
import datetime
import pytz
from presentation.bokeh_graph_creator import BokehGraphCreator
from streamlit_bokeh import streamlit_bokeh

from domain.material_type import MaterialType
from infra.graph_repository_factory import ApiHostName, GraphRepositoryFactory
from domain.graph import Axis, AxisRange, AxisType

def main(material_type: MaterialType):
    st.title(f"{material_type.value.capitalize()} material data")

    limit = st.sidebar.number_input(
        "Limit", min_value=1, max_value=100, value=10, step=1
    )
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
        date_from_str = date_from_dt.isoformat()
    else:
        date_from_str = None

    if date_to:
        date_to_dt = datetime.datetime.combine(date_to, datetime.time(23, 59, 59))
        date_to_dt = user_timezone.localize(date_to_dt)
        date_to_str = date_to_dt.isoformat()
    else:
        date_to_str = None

    # graph_data_service = GraphDataService(
    #     STARRYDATA_BULK_DATA_API=os.environ.get("STARRYDATA_BULK_DATA_API", ""),
    #     STARRYDATA2_API_XY_DATA=os.environ.get("STARRYDATA2_API_XY_DATA", "")
    # )


    # configファイルをPythonファイルから読み込む
    if material_type.value == MaterialType.THERMOELECTRIC.value:
        from domain.thermoelectric import THERMOELECTRIC_GRAPHS as CONFIG_GRAPHS
    elif material_type.value == MaterialType.BATTERY.value:
        from domain.battery import BATTERY_GRAPHS as CONFIG_GRAPHS
    else:
        CONFIG_GRAPHS = []

    # graph_repository = GraphRepositoryFactory.create(ApiHostName.CLEANSING_DATASET)
    # base_graph = graph_repository.get_graph_by_property(
    #     material_type=material_type,
    #     property_x=CONFIG_GRAPHS[0].x_axis.property,
    #     property_y=CONFIG_GRAPHS[0].y_axis.property
    # )

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

    graph_creator = BokehGraphCreator(GraphDataService())
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
    bokeh_figure = graph_creator.create_bokeh_figure(
        x_axis=new_x_axis,
        y_axis=new_y_axis
    )

    # graph_service = StreamlitGraphCreator()
    # figure = graph_service.create_bokeh_graph(base_graph)
    # base_data_source = graph_service.create_bokeh_data_source(base_graph)
    # base_renderer = figure.circle(
    #     "x",
    #     "y",
    #     source=base_data_source,
    #     fill_color="blue",
    #     fill_alpha=1,
    #     size=2,
    #     line_width=0,
    #     line_color="#3288bd",
    # )


    # div, script, title, figure = graph_service.create_bokeh_graph(
    #     base_data,
    #     highlight_points,
    #     highlight_lines,
    #     sizef_points,
    #     line_sizef_points,
    #     x_end,
    #     y_end,
    #     label,
    #     widths,
    #     y_scale,
    #     [x_min, x_max],
    #     [y_min, y_max],
    #     x_scale,
    #     material_type=material_type,
    # )

    st.subheader(f"Graph: {prop_x} vs {prop_y}")



    # from bokeh.plotting import figure
    # from bokeh.models import ColumnDataSource
    # x = [1, 2, 3, 4, 5]
    # y = [2, 4, 8, 16, 32]
    # source = ColumnDataSource(data=dict(x=x, y=y))

    # YOUR_BOKEH_FIGURE = figure(title="Simple Line Example",
    #                     x_axis_label="x",
    #                     y_axis_label="y")
    # YOUR_BOKEH_FIGURE.scatter(x='x', y='y', source=source, legend_label="Trend", line_width=2)



    streamlit_bokeh(bokeh_figure, use_container_width=True, theme="streamlit", key="my_unique_key")
