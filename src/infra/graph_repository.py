import os

import requests
from domain.graph import XYPoint, XYPoints, XYSeries, GraphRepository
from infra.api_client import Starrydata2ApiClient, CleansingDatasetApiClient, XYApiResponse


class GraphRepositoryApiStarrydata2(GraphRepository):
    def __init__(self, api_client=None):
        host = os.environ.get("STARRYDATA2_API_XY_DATA")
        if not host:
            raise ValueError("STARRYDATA2_API_XY_DATA environment variable is not set.")
        self.api_client = api_client or Starrydata2ApiClient(host)

    def get_graph_by_property(self, property_x: str, property_y: str) -> XYSeries:
        # API呼び出し・データ取得処理は省略（必要に応じて実装）
        return XYSeries(data=[])

    def get_graph_by_property_and_unit(self, property_x: str, property_y: str, unit_x: str, unit_y: str) -> XYSeries:
        """
        bulk data apiはJST前日0時のバックアップなので、
        最新データはJSTで前日0時以降のデータのみ取得すれば全件網羅できる。
        date_from, date_toが指定されていない場合は、date_fromをJST前日0時、date_toを現在時刻に自動設定する。
        """

        import pytz
        from datetime import datetime, timedelta
        JST = pytz.timezone('Asia/Tokyo')
        now = datetime.now(JST)
        date_from_dt = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        date_from = date_from_dt.isoformat()
        date_to = now.isoformat()
        params = {
            "property_x": property_x,
            "property_y": property_y,
            "unit_x": unit_x,
            "unit_y": unit_y,
            "date_from": date_from,
            "date_to": date_to,
            "limit": 100
        }
        api_data: XYApiResponse = self.api_client.fetch_xy_data(params)
        x_lists = api_data.x
        y_lists = api_data.y
        updated_at_lists = api_data.updated_at
        sid_lists = api_data.SID or [str(i) for i in range(len(x_lists))]
        xy_series = []
        for i, (x_list, y_list) in enumerate(zip(x_lists, y_lists)):
            if x_list and y_list and len(x_list) == len(y_list):
                if not (updated_at_lists and i < len(updated_at_lists)):
                    raise ValueError("updated_at is required for each data series, but missing at index {}".format(i))
                updated_at = updated_at_lists[i]
                figure_id = api_data.figure_id[i]
                sample_id = api_data.sample_id[i]
                composition = api_data.composition[i]
                points = [XYPoint(x=xi, y=yi) for xi, yi in zip(x_list, y_list)]
                xy_series.append(XYPoints(data=points, updated_at=updated_at, sid=sid_lists[i], figure_id=figure_id, sample_id=sample_id, composition=composition))
        return XYSeries(data=xy_series)

class GraphRepositoryApiCleansingDataset(GraphRepository):
    def __init__(self, api_client=None):
        host = os.environ.get("STARRYDATA_BULK_DATA_API")
        if not host:
            raise ValueError("STARRYDATA_BULK_DATA_API environment variable is not set.")
        self.api_client = api_client or CleansingDatasetApiClient(host)

    def get_graph_by_property(self, property_x: str, property_y: str) -> XYSeries:
        api_data: XYApiResponse = self.api_client.fetch_xy_data(property_x, property_y)
        x_lists = api_data.x
        y_lists = api_data.y
        updated_at_lists = api_data.updated_at
        sid_lists = api_data.SID or [str(i) for i in range(len(x_lists))]
        xy_series = []
        for i, (x_list, y_list) in enumerate(zip(x_lists, y_lists)):
            if x_list and y_list and len(x_list) == len(y_list):
                if not (updated_at_lists and i < len(updated_at_lists)):
                    raise ValueError("updated_at is required for each data series, but missing at index {}".format(i))
                updated_at = updated_at_lists[i]
                figure_id = api_data.figure_id[i]
                sample_id = api_data.sample_id[i]
                composition = api_data.composition[i]
                points = [XYPoint(x=xi, y=yi) for xi, yi in zip(x_list, y_list)]
                xy_series.append(XYPoints(data=points, updated_at=updated_at, sid=sid_lists[i], figure_id=figure_id, sample_id=sample_id, composition=composition))
        return XYSeries(data=xy_series)

    def get_graph_by_property_and_unit(self, property_x: str, property_y: str, unit_x: str, unit_y: str) -> XYSeries:
        raise NotImplementedError("get_graph_by_property_and_unit is not implemented for bulk data API.")
