from typing import List, Dict, Any

class GraphDataPoint:
    def __init__(self, x: float, y: float, sid: int):
        self.x = x
        self.y = y
        self.sid = sid

class Graph:
    def __init__(
        self,
        prop_x: str,
        prop_y: str,
        unit_x: str,
        unit_y: str,
        data_points: List[GraphDataPoint],
        y_scale: str,
        x_range: List[float],
        y_range: List[float],
    ):
        self.prop_x = prop_x
        self.prop_y = prop_y
        self.unit_x = unit_x
        self.unit_y = unit_y
        self.data_points = data_points
        self.y_scale = y_scale
        self.x_range = x_range
        self.y_range = y_range

    def validate(self) -> bool:
        # 例: データポイントが空でないことを検証
        return len(self.data_points) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prop_x": self.prop_x,
            "prop_y": self.prop_y,
            "unit_x": self.unit_x,
            "unit_y": self.unit_y,
            "data_points": [
                {"x": dp.x, "y": dp.y, "sid": dp.sid} for dp in self.data_points
            ],
            "y_scale": self.y_scale,
            "x_range": self.x_range,
            "y_range": self.y_range,
        }
