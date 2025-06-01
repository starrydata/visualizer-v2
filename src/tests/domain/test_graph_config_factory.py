import pytest
from domain.graph_config_factory import get_graph_configs
from domain.material_type import MaterialType
from domain.thermoelectric import THERMOELECTRIC_GRAPHS
from domain.battery import BATTERY_GRAPHS
from src.tests.domain.graph_mock_factory import make_xy_points
from src.domain.graph import XYPoint

def test_get_graph_configs_thermoelectric():
    result = get_graph_configs(MaterialType.THERMOELECTRIC)
    assert result == THERMOELECTRIC_GRAPHS

def test_get_graph_configs_battery():
    result = get_graph_configs(MaterialType.BATTERY)
    assert result == BATTERY_GRAPHS

def test_get_graph_configs_unknown_typeerror():
    with pytest.raises(TypeError):
        get_graph_configs(object())  # type: ignore

def test_make_xy_points():
    points = make_xy_points([XYPoint(1, 2)], updated_at="2024-01-01T00:00:00Z", sid="test-sid")
    assert points.data[0].x == 1
    assert points.data[0].y == 2
    assert points.updated_at == "2024-01-01T00:00:00Z"
    assert points.sid == "test-sid"

