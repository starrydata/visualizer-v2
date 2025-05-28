import pytest
from domain.graph import Graph, XYData

def test_graph_data_point():
    dp = XYData(1.0, 2.0, 100)
    assert dp.x == 1.0
    assert dp.y == 2.0
    assert dp.sid == 100

def test_graph_validation():
    graph = Graph(
        prop_x="X",
        prop_y="Y",
        unit_x="units",
        unit_y="units",
        xy_data=[XYData(1, 2, 3)],
        y_scale="linear",
        x_range=[0, 10],
        y_range=[0, 10],
    )
    assert graph.validate() is True

    empty_graph = Graph(
        prop_x="X",
        prop_y="Y",
        unit_x="units",
        unit_y="units",
        xy_data=[],
        y_scale="linear",
        x_range=[0, 10],
        y_range=[0, 10],
    )
    assert empty_graph.validate() is False
