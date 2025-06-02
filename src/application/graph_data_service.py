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
    is_highlighted: bool
    sid: str
    figure_id: str
    sample_id: str
    composition: str

@dataclass
class XYSeriesDTO:
    data: List[XYPointsDTO]

class GraphDataService:
    def filter_and_sort_by_highlight_dto(self, xy_series: XYSeries, highlight_condition: HighlightCondition) -> XYSeriesDTO:
        """
        ハイライト条件でXYPointsを2分割し、各XYPointsDTOにis_highlighted属性を付与し、ハイライト対象を末尾に並べる（非ハイライト→ハイライトの順）
        """
        highlighted = []
        non_highlighted = []
        for points in xy_series.data:
            is_highlight = highlight_condition.is_match_points(points)
            dto = XYPointsDTO(
                data=points.data,
                is_highlighted=is_highlight,
                sid=points.sid,
                figure_id=points.figure_id,
                sample_id=points.sample_id,
                composition=points.composition
            )
            if is_highlight:
                highlighted.append(dto)
            else:
                non_highlighted.append(dto)
        return XYSeriesDTO(data=non_highlighted + highlighted)

    def _convert_utc_to_jst(self, updated_at: str) -> str:
        from datetime import datetime, timezone, timedelta
        import re
        # Z→+00:00
        s = updated_at
        if s.endswith('Z'):
            s = s[:-1] + '+00:00'
        if not re.search(r'[+-]\d{2}:\d{2}$', s):
            dt = datetime.fromisoformat(s)
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = datetime.fromisoformat(s)
        # JSTに変換
        jst = dt.astimezone(timezone(timedelta(hours=9)))
        # 2025-06-02T23:59:59+0900 の形式で返す
        return jst.strftime('%Y-%m-%dT%H:%M:%S%z')

    def _replace_points_with_jst(self, points_list):
        from src.domain.graph import XYPoints
        new_list = []
        for points in points_list:
            new_list.append(
                XYPoints(
                    data=points.data,
                    updated_at=self._convert_utc_to_jst(points.updated_at),
                    sid=points.sid,
                    figure_id=points.figure_id,
                    sample_id=points.sample_id,
                    composition=points.composition if points.composition is not None else ""
                )
            )
        return new_list

    def get_merged_graph_data(
        self,
        prop_x: str,
        prop_y: str,
        unit_x: str = "",
        unit_y: str = "",
        highlight_condition: Optional[HighlightCondition] = None,
    ) -> XYSeriesDTO:
        repo_bulk = GraphRepositoryFactory.create(ApiHostName.CLEANSING_DATASET)
        bulk_data_series = repo_bulk.get_graph_by_property(prop_x, prop_y)
        # bulk側はJST変換不要
        repo_today = GraphRepositoryFactory.create(ApiHostName.STARRYDATA2)
        today_data_series = repo_today.get_graph_by_property_and_unit(
            property_x=prop_x,
            property_y=prop_y,
            unit_x=unit_x,
            unit_y=unit_y,
        )
        # today側のみJST変換
        today_data_series = XYSeries(data=self._replace_points_with_jst(today_data_series.data))
        bulk_data_series.data.extend(today_data_series.data)
        if highlight_condition is not None:
            return self.filter_and_sort_by_highlight_dto(bulk_data_series, highlight_condition)
        dtos = []
        for points in bulk_data_series.data:
            dtos.append(XYPointsDTO(
                data=points.data,
                is_highlighted=False,
                sid=points.sid,
                figure_id=points.figure_id,
                sample_id=points.sample_id,
                composition=points.composition if points.composition is not None else ""
            ))
        return XYSeriesDTO(data=dtos)

