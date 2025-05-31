import os
import datetime
import requests
from typing import Dict, List, Tuple

class GraphDataService:
    # def __init__(self, base_data_uri: str, highlight_data_uri: str):
    #     self.base_data_uri = base_data_uri
    #     self.highlight_data_uri = highlight_data_uri

    # def load_config(self, material_type: str) -> Dict:
    #     config_path = os.path.join(os.path.dirname(__file__), f"../config.{material_type}.json")
    #     import json
    #     with open(config_path, "r", encoding="utf-8") as f:
    #         return json.load(f)

    # def fetch_base_data(self, prop_x: str, prop_y: str) -> Dict:
    #     json_path = f"{self.base_data_uri}/{prop_x}-{prop_y}.json"
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
