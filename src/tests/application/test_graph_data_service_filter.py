import pytest
from src.domain.graph import XYPoint, XYPoints, XYSeries, DateHighlightCondition, HighlightCondition
from src.application.graph_data_service import GraphDataService, XYPointsDTO, XYSeriesDTO
from src.tests.domain.graph_mock_factory import make_xy_points

class DummyHighlightCondition(HighlightCondition):
    def is_match_points(self, points: XYPoints) -> bool:
        # ハイライト条件: updated_atが"2024-01-02"の日付
        return points.updated_at[:10] == "2024-01-02"

def test_filter_and_sort_by_highlight():
    # 3つのXYPoints: 1つだけハイライト対象
    points1 = make_xy_points([XYPoint(1, 2)], updated_at="2024-01-01T00:00:00Z")
    points2 = make_xy_points([XYPoint(3, 4)], updated_at="2024-01-02T00:00:00Z")  # ハイライト対象
    points3 = make_xy_points([XYPoint(5, 6)], updated_at="2024-01-03T00:00:00Z")
    series = XYSeries([points1, points2, points3])
    service = GraphDataService()
    cond = DummyHighlightCondition()
    result: XYSeriesDTO = service.filter_and_sort_by_highlight_dto(series, cond)
    # ハイライト対象(points2)がラストに来ていること
    assert result.data[2].data == points2.data
    assert result.data[2].is_highlighted is True
    assert set(tuple(dto.data) for dto in result.data[:2]) == {tuple(points1.data), tuple(points3.data)}
    assert all(dto.is_highlighted is False for dto in result.data[:2])

def test_filter_and_sort_by_highlight_all():
    # 全てハイライト対象
    points1 = make_xy_points([XYPoint(1, 2)], updated_at="2024-01-02T00:00:00Z")
    points2 = make_xy_points([XYPoint(3, 4)], updated_at="2024-01-02T12:00:00Z")
    series = XYSeries([points1, points2])
    service = GraphDataService()
    cond = DummyHighlightCondition()
    result: XYSeriesDTO = service.filter_and_sort_by_highlight_dto(series, cond)
    assert [dto.data for dto in result.data] == [points1.data, points2.data]
    assert all(dto.is_highlighted for dto in result.data)

def test_filter_and_sort_by_highlight_none():
    # 全て非ハイライト
    points1 = make_xy_points([XYPoint(1, 2)], updated_at="2024-01-01T00:00:00Z")
    points2 = make_xy_points([XYPoint(3, 4)], updated_at="2024-01-03T00:00:00Z")
    series = XYSeries([points1, points2])
    service = GraphDataService()
    cond = DummyHighlightCondition()
    result: XYSeriesDTO = service.filter_and_sort_by_highlight_dto(series, cond)
    assert [dto.data for dto in result.data] == [points1.data, points2.data]
    assert all(dto.is_highlighted is False for dto in result.data)
