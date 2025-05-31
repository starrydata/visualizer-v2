import pytest
from infra.graph_repository import get_graphs_by_material_type
from domain.material_type import MaterialType

def test_get_graphs_by_material_type_thermoelectric():
    graphs = get_graphs_by_material_type(MaterialType.THERMOELECTRIC)
    assert graphs is not None
    assert len(graphs) > 0
    # 代表的なpropertyを確認
    assert graphs[0].x_axis.property == "Temperature"

def test_get_graphs_by_material_type_battery():
    graphs = get_graphs_by_material_type(MaterialType.BATTERY)
    assert graphs is not None
    assert len(graphs) > 0
    # 代表的なpropertyを確認
    assert hasattr(graphs[0].x_axis, "property")

def test_get_graphs_by_material_type_invalid():
    class DummyMaterialType:
        pass
    with pytest.raises(ValueError) as excinfo:
        get_graphs_by_material_type(DummyMaterialType())
    assert "Unknown material_type" in str(excinfo.value)
