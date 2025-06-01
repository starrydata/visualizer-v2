from typing import List
from pydantic import BaseModel

# XYApiResponseは下記APIレスポンス仕様を参考にしています：
# - https://starrydata.github.io/bulk-data-api/v1/index.html#/default/get__prop_x___prop_y__json
# - https://www.starrydata2.org/paperlist/openapi/#/default/get_xy_data_api_
class XYApiResponse(BaseModel):
    x: List[List[float]]
    y: List[List[float]]
    updated_at: List[str]
    SID: List[str]
    figure_id: List[str]
    sample_id: List[str]
    composition: List[str]

class Starrydata2ApiClient:
    def __init__(self, host: str):
        self.host = host

    def fetch_xy_data(self, params: dict) -> XYApiResponse:
        import requests
        response = requests.get(f"{self.host}/", params=params)
        response.raise_for_status()
        data = response.json().get("data", {})
        return XYApiResponse(**data)

class CleansingDatasetApiClient:
    def __init__(self, host: str):
        self.host = host

    def fetch_xy_data(self, property_x: str, property_y: str) -> XYApiResponse:
        import requests
        path = f"{self.host}/{property_x}-{property_y}.json"
        response = requests.get(path)
        response.raise_for_status()
        data = response.json().get("data", {})
        return XYApiResponse(**data)
