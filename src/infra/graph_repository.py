import os

import requests
from domain.graph import Axis, AxisRange, AxisType, DataPoint, DataPoints, Graph, GraphRepository
from typing import List
from domain.thermoelectric import THERMOELECTRIC_GRAPHS
from domain.battery import BATTERY_GRAPHS
from domain.material_type import MaterialType

# NOTE: Repositoryクラス本体に持つべきメソッドな気がするが、具象な実装をdomain layerに書くとloopのimportが発生したため、一旦ここに
def get_graphs_by_material_type(material_type):
    # 文字列で渡ってきた場合はEnumに変換
    if material_type.value == MaterialType.THERMOELECTRIC.value:
        return THERMOELECTRIC_GRAPHS
    elif material_type.value == MaterialType.BATTERY.value:
        return BATTERY_GRAPHS
    else:
        raise ValueError(f"Unknown material_type: {material_type}")

class GraphRepositoryApiStarrydata2(GraphRepository):
    def get_graph_by_property(self, material_type, property_x, property_y):
        return super().get_graph_by_property(material_type, property_x, property_y)

    def get_graph_by_property_and_unit(self, material_type: MaterialType, property_x: str, property_y: str, unit_x: str, unit_y: str, date_from: str, date_to: str, limit: int) -> Graph:
        target_material_graphs = get_graphs_by_material_type(material_type)
        target_graph = None
        for graph in target_material_graphs:
            if graph.x_axis.property == property_x and graph.y_axis.property == property_y:
                target_graph = graph
                break
        if target_graph is None:
            raise ValueError(f"Graph with properties {property_x} and {property_y} not found for material type {material_type}")
        host = os.environ.get("HIGHLIGHT_DATA_URI")
        params = {
            "property_x": property_x,
            "property_y": property_y,
            "unit_x": unit_x,
            "unit_y": unit_y,
            "date_from": date_from,
            "date_to": date_to,
            "limit": limit
        }
        response = requests.get(f"{host}/", params=params)
        response.raise_for_status()
        data = response.json().get("data", {})
        x_lists = data.get("x", [])
        y_lists = data.get("y", [])

        # 正しい: 各x_list, y_listのペアごとにDataPointsを作成
        for x_list, y_list in zip(x_lists, y_lists):
            if x_list and y_list and len(x_list) == len(y_list):
                points = [DataPoint(x=xi, y=yi) for xi, yi in zip(x_list, y_list)]
                target_graph.data_point_series.append(DataPoints(data_points=points))
        target_graph.x_axis.unit = unit_x
        target_graph.y_axis.unit = unit_y
        return target_graph

class GraphRepositoryApiCleansingDataset(GraphRepository):
    def get_graph_by_property(self, material_type: MaterialType, property_x: str, property_y: str) -> Graph:
        target_material_graphs = get_graphs_by_material_type(material_type)
        target_graph = None
        for graph in target_material_graphs:
            if graph.x_axis.property == property_x and graph.y_axis.property == property_y:
                target_graph = graph
                break
        if target_graph is None:
            raise ValueError(f"Graph with properties {property_x} and {property_y} not found for material type {material_type}")
        host = os.environ.get("BASE_DATA_URI")
        path = f"{host}/{property_x}-{property_y}.json"
        response = requests.get(path)
        response.raise_for_status()
        data = response.json().get("data", {})
        x_lists = data.get("x", [])
        y_lists = data.get("y", [])
        # 各x, yリストのペアでDataPointsを作成
        target_graph.data_point_series = []
        for x_list, y_list in zip(x_lists, y_lists):
            if x_list and y_list and len(x_list) == len(y_list):
                points = [DataPoint(x=xi, y=yi) for xi, yi in zip(x_list, y_list)]
                target_graph.data_point_series.append(DataPoints(data_points=points))
        return target_graph

    def get_graph_by_property_and_unit(self, material_type: MaterialType, property_x: str, unit_x: str, property_y: str, unit_y: str) -> Graph:
        self.super().get_graph_by_property_and_unit(material_type, property_x, unit_x, property_y, unit_y)
