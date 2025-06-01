import os
import datetime
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from infra.graph_repository_factory import ApiHostName, GraphRepositoryFactory
from src.domain.graph import XYSeries, XYPoints, XYPoint
from src.domain.graph import HighlightCondition

@dataclass
class XYPointsDTO:
    data: List[XYPoint]
    is_highlighted: bool = False

@dataclass
class XYSeriesDTO:
    data: List[XYPointsDTO]

class GraphDataService:
    # def __init__(self, STARRYDATA_BULK_DATA_API: str, STARRYDATA2_API_XY_DATA: str):
    #     self.STARRYDATA_BULK_DATA_API = STARRYDATA_BULK_DATA_API
    #     self.STARRYDATA2_API_XY_DATA = STARRYDATA2_API_XY_DATA

    # def load_config(self, material_type: str) -> Dict:
    #     config_path = os.path.join(os.path.dirname(__file__), f"../config.{material_type}.json")
    #     import json
    #     with open(config_path, "r", encoding="utf-8") as f:
    #         return json.load(f)

    # def fetch_base_data(self, prop_x: str, prop_y: str) -> Dict:
    #     json_path = f"{self.STARRYDATA_BULK_DATA_API}/{prop_x}-{prop_y}.json"
    #     response = requests.get(json_path)
    #     response.raise_for_status()
    #     return response.json()

    def process_highlight_data(self, highlight_data: Dict) -> Tuple[Dict, Dict, List[float], List[float], List[float], List[float], List[str], List[float]]:
        highlight_points = {
            "x": highlight_data.get("x", []),
            "y": highlight_data.get("y", []),
            "SID": highlight_data.get("SID", []),
            "updated_at": highlight_data.get("updated_at", []),
        }
        highlight_lines = {
            "x": highlight_data.get("x", []),
            "y": highlight_data.get("y", []),
            "SID": highlight_data.get("SID", []),
            "figure_id": highlight_data.get("figure_id", []),
            "sample_id": highlight_data.get("sample_id", []),
            "updated_at": highlight_data.get("updated_at", []),
        }

        ts_points = [int(datetime.datetime.fromisoformat(t).timestamp() * 1000) for t in highlight_points.get("updated_at", [])]
        mi_points = min(ts_points) if ts_points else 0
        ma_points = max(ts_points) if ts_points else 0

        sizef_points = []
        line_sizef_points = []
        for t in ts_points:
            sizef_points.append(2 + ((t - mi_points) / (ma_points - mi_points)) * 4 if ma_points > mi_points else 2)
            line_sizef_points.append(0.1 + ((t - mi_points) / (ma_points - mi_points)) * 0.4 if ma_points > mi_points else 0.1)

        x_end = []
        y_end = []
        label = []
        widths = []
        for i in range(len(highlight_lines.get("x", []))):
            xs = highlight_lines["x"][i]
            ys = highlight_lines["y"][i]
            x_end.append(xs[-1] if xs else None)
            y_end.append(ys[-1] if ys else None)
            sid = highlight_lines.get("SID", [])[i] if i < len(highlight_lines.get("SID", [])) else ""
            figure_id = highlight_lines.get("figure_id", [])[i] if i < len(highlight_lines.get("figure_id", [])) else ""
            sample_id = highlight_lines.get("sample_id", [])[i] if i < len(highlight_lines.get("sample_id", [])) else ""
            label.append(f"{sid}-{figure_id}-{sample_id}")

        ts_lines = [int(datetime.datetime.fromisoformat(t).timestamp() * 1000) for t in highlight_lines.get("updated_at", [])]
        mi_lines = min(ts_lines) if ts_lines else 0
        ma_lines = max(ts_lines) if ts_lines else 0

        for t in ts_lines:
            widths.append(0.1 + ((t - mi_lines) / (ma_lines - mi_lines)) * 0.2 if ma_lines > mi_lines else 0.1)

        return highlight_points, highlight_lines, sizef_points, line_sizef_points, x_end, y_end, label, widths

    def filter_and_sort_by_highlight_dto(self, xy_series: XYSeries, highlight_condition: HighlightCondition) -> XYSeriesDTO:
        """
        ハイライト条件でXYPointsを2分割し、各XYPointsDTOにis_highlighted属性を付与し、ハイライト対象を末尾に並べる（非ハイライト→ハイライトの順）
        """
        highlighted = []
        non_highlighted = []
        for points in xy_series.data:
            is_highlight = highlight_condition.is_match_points(points)
            dto = XYPointsDTO(data=points.data, is_highlighted=is_highlight)
            if is_highlight:
                highlighted.append(dto)
            else:
                non_highlighted.append(dto)
        return XYSeriesDTO(data=non_highlighted + highlighted)

    def get_merged_graph_data(
        self,
        prop_x: str,
        prop_y: str,
        unit_x: str = "",
        unit_y: str = "",
        highlight_condition: Optional[HighlightCondition] = None,
    ) -> XYSeriesDTO:
        """
        repositoryを使ってbulk data（全件）と今日のデータ（date_from, date_toで絞る）を取得し、DTOで返す
        highlight_conditionが指定されていれば、ハイライト対象を先頭に並べる
        """
        # Bulk data（全件）
        repo_bulk = GraphRepositoryFactory.create(ApiHostName.CLEANSING_DATASET)
        bulk_data_series = repo_bulk.get_graph_by_property(prop_x, prop_y)

        # 今日のデータ（date_from, date_to, unit_x, unit_y指定）
        repo_today = GraphRepositoryFactory.create(ApiHostName.STARRYDATA2)
        today_data_series = repo_today.get_graph_by_property_and_unit(
            property_x=prop_x,
            property_y=prop_y,
            unit_x=unit_x,
            unit_y=unit_y,
        )

        # 統合する
        bulk_data_series.data.extend(today_data_series.data)

        # ハイライト条件で並び替え・DTO化
        if highlight_condition is not None:
            return self.filter_and_sort_by_highlight_dto(bulk_data_series, highlight_condition)
        # ハイライトなしの場合もDTO化
        dtos = []
        for points in bulk_data_series.data:
            dtos.append(XYPointsDTO(data=points.data, is_highlighted=False))
        return XYSeriesDTO(data=dtos)

