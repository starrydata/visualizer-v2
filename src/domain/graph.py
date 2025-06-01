from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
from abc import ABC, abstractmethod

class AxisType(Enum):
    """軸のスケール種別を表す列挙型"""
    LINEAR = "linear"
    LOGARITHMIC = "log"
    # 例: SYMLOG = "symlog" など将来追加可能

    def is_log(self) -> bool:
        """対数軸かどうかを判定"""
        return self == AxisType.LOGARITHMIC


@dataclass
class AxisRange:
    min_value: float
    max_value: float


@dataclass(frozen=False)
class Axis:
    """グラフの軸を表すクラス"""
    property: str
    axis_type: AxisType
    unit: str
    axis_range: AxisRange


@dataclass(frozen=True)
class XYPoint:
    x: float
    y: float

@dataclass(frozen=True)
class  XYPoints:
    data: List[XYPoint]
    updated_at: str  # ISO8601文字列（必須）
    sid: str         # 識別子（必須）

@dataclass(frozen=True)
class XYSeries:
    data: List[XYPoints]


@dataclass(frozen=False)
class Graph():
    x_axis: Axis
    y_axis: Axis
    data: XYSeries


class GraphRepository(ABC):
    """グラフデータのリポジトリインターフェース"""
    @abstractmethod
    def get_graph_by_property(self, property_x: str, property_y: str) -> XYSeries:
        """指定されたプロパティに基づいてグラフを取得する"""
        pass

    @abstractmethod
    def get_graph_by_property_and_unit(
        self,
        property_x: str,
        property_y: str,
        unit_x: str,
        unit_y: str
    ) -> XYSeries:
        """指定されたプロパティと単位に基づいてグラフを取得する"""
        pass

class HighlightCondition(ABC):
    """データ点のハイライト条件の抽象基底クラス"""
    def is_match_points(self, points):
        """
        ダミー実装（後方互換性のため）
        """
        raise NotImplementedError("Use is_match_points for batch operations.")

@dataclass(frozen=True)
class DateHighlightCondition(HighlightCondition):
    date_from: str  # ISO8601形式の日付（YYYY-MM-DD）
    date_to: str    # ISO8601形式の日付（YYYY-MM-DD）

    def is_match_points(self, points: XYPoints) -> bool:
        """
        XYPoints（データ点のまとまり）がハイライト対象か判定。
        XYPointsのupdated_atを使う。
        """
        if not hasattr(points, 'updated_at') or not points.updated_at:
            return False
        point_date = points.updated_at[:10]
        return self.date_from <= point_date <= self.date_to

@dataclass(frozen=True)
class SIDHighlightCondition(HighlightCondition):
    sid: str
    def is_match_points(self, points: XYPoints) -> bool:
        return getattr(points, "sid", None) == self.sid

# 今後の拡張例:
# @dataclass(frozen=True)
# class CompositionHighlightCondition(HighlightCondition):
#     composition: str
#     def is_match(self, point: XYPoint) -> bool:
#         return getattr(point, "composition", None) == self.composition

