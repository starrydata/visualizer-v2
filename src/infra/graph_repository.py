import os

import requests
from domain.graph import DataPoint, DataPoints, GraphRepository
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
    def get_graph_by_property(self, property_x, property_y):
        return super().get_graph_by_property(property_x, property_y)

    def get_graph_by_property_and_unit(self, property_x: str, property_y: str, unit_x: str, unit_y: str) -> List[DataPoints]:
        """
        bulk data apiはJST前日0時のバックアップなので、
        最新データはJSTで前日0時以降のデータのみ取得すれば全件網羅できる。
        date_from, date_toが指定されていない場合は、date_fromをJST前日0時、date_toを現在時刻に自動設定する。
        """
        import pytz
        from datetime import datetime, timedelta
        JST = pytz.timezone('Asia/Tokyo')
        now = datetime.now(JST)
        # 前日0時
        date_from_dt = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        date_from = date_from_dt.isoformat()
        date_to = now.isoformat()
        # target_material_graphs = get_graphs_by_material_type(material_type)
        # target_graph = None
        # for graph in target_material_graphs:
        #     if graph.x_axis.property == property_x and graph.y_axis.property == property_y:
        #         target_graph = graph
        #         break
        # if target_graph is None:
        #     raise ValueError(f"Graph with properties {property_x} and {property_y} not found for material type {material_type}")
        host = os.environ.get("STARRYDATA2_API_XY_DATA")
        params = {
            "property_x": property_x,
            "property_y": property_y,
            "unit_x": unit_x,
            "unit_y": unit_y,
            "date_from": date_from,
            "date_to": date_to,
            "limit": 100 # 上限値を設定
        }
        response = requests.get(f"{host}/", params=params)
        response.raise_for_status()
        data = response.json().get("data", {})
        x_lists = data.get("x", [])
        y_lists = data.get("y", [])

        # 正しい: 各x_list, y_listのペアごとにDataPointsを作成
        data_point_series = []
        for x_list, y_list in zip(x_lists, y_lists):
            if x_list and y_list and len(x_list) == len(y_list):
                points = [DataPoint(x=xi, y=yi) for xi, yi in zip(x_list, y_list)]
                data_point_series.append(DataPoints(data_points=points))

        return data_point_series

class GraphRepositoryApiCleansingDataset(GraphRepository):
    def get_graph_by_property(self, property_x: str, property_y: str) -> List[DataPoints]:
        # target_material_graphs = get_graphs_by_material_type(material_type)
        # target_graph = None
        # for graph in target_material_graphs:
        #     if graph.x_axis.property == property_x and graph.y_axis.property == property_y:
        #         target_graph = graph
        #         break
        # if target_graph is None:
        #     raise ValueError(f"Graph with properties {property_x} and {property_y} not found for material type {material_type}")
        host = os.environ.get("STARRYDATA_BULK_DATA_API")
        path = f"{host}/{property_x}-{property_y}.json"
        response = requests.get(path)
        response.raise_for_status()
        data = response.json().get("data", {})
        x_lists = data.get("x", [])
        y_lists = data.get("y", [])
        # 各x, yリストのペアでDataPointsを作成
        data_point_series = []
        for x_list, y_list in zip(x_lists, y_lists):
            if x_list and y_list and len(x_list) == len(y_list):
                points = [DataPoint(x=xi, y=yi) for xi, yi in zip(x_list, y_list)]
                data_point_series.append(DataPoints(data_points=points))
        return data_point_series

    def get_graph_by_property_and_unit(self, property_x: str, property_y: str, unit_x: str, unit_y: str) -> List[DataPoints]:
        # このAPIは未実装。例外を投げて明示する。
        raise NotImplementedError("get_graph_by_property_and_unit is not implemented for bulk data API.")
