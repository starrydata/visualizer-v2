import pytest
from domain.graph_config_factory import get_graph_configs
from domain.material_type import MaterialType
from domain.thermoelectric import THERMOELECTRIC_GRAPHS
from domain.battery import BATTERY_GRAPHS

def test_get_graph_configs_thermoelectric():
    result = get_graph_configs(MaterialType.THERMOELECTRIC)
    assert result == THERMOELECTRIC_GRAPHS

def test_get_graph_configs_battery():
    result = get_graph_configs(MaterialType.BATTERY)
    assert result == BATTERY_GRAPHS

def test_get_graph_configs_unknown_typeerror():
    with pytest.raises(TypeError):
        get_graph_configs(object())  # type: ignore

