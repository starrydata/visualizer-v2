from domain.material_type import MaterialType
from domain.thermoelectric import THERMOELECTRIC_GRAPHS
from domain.battery import BATTERY_GRAPHS

def get_graph_configs(material_type: MaterialType):
    if not isinstance(material_type, MaterialType):
        raise TypeError("material_type must be an instance of MaterialType Enum")
    if material_type == MaterialType.THERMOELECTRIC:
        return THERMOELECTRIC_GRAPHS
    elif material_type == MaterialType.BATTERY:
        return BATTERY_GRAPHS
