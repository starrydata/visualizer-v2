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
            dtos.append(XYPointsDTO(
                data=points.data,
                is_highlighted=False,
                sid=points.sid,
                figure_id=points.figure_id,
                sample_id=points.sample_id,
                composition=points.composition
            ))
        return XYSeriesDTO(data=dtos)

