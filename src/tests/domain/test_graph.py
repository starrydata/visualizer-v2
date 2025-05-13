import pytest
from domain.graph import Graph, GraphDataPoint

def test_graph_data_point():
    dp = GraphDataPoint(1.0, 2.0, 100)
    assert dp.x == 1.0
    assert dp.y == 2.0
    assert dp.sid == 100

def test_graph_validation():
    graph = Graph(
        prop_x="X",
        prop_y="Y",
        unit_x="units",
        unit_y="units",
        data_points=[GraphDataPoint(1, 2, 3)],
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
        data_points=[],
        y_scale="linear",
        x_range=[0, 10],
        y_range=[0, 10],
    )
    assert empty_graph.validate() is False
