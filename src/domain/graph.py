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
class DataPoint:
    x: float
    y: float
    updated_at: str  # ISO8601文字列（必須）

@dataclass(frozen=True)
class  DataPoints:
    data: List[DataPoint]

@dataclass(frozen=True)
class DataPointsSeries:
    data: List[DataPoints]


@dataclass(frozen=False)
class Graph():
    x_axis: Axis
    y_axis: Axis
    data_points_series: List[DataPoints]


class GraphRepository(ABC):
    """グラフデータのリポジトリインターフェース"""
    @abstractmethod
    def get_graph_by_property(self, property_x: str, property_y: str) -> DataPointsSeries:
        """指定されたプロパティに基づいてグラフを取得する"""
        pass

    @abstractmethod
    def get_graph_by_property_and_unit(
        self,
        property_x: str,
        property_y: str,
        unit_x: str,
        unit_y: str
    ) -> DataPointsSeries:
        """指定されたプロパティと単位に基づいてグラフを取得する"""
        pass

