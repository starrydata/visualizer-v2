

from domain.graph import GraphRepository
from infra.graph_repository import GraphRepositoryApiStarrydata2, GraphRepositoryApiCleansingDataset
from enum import Enum

class ApiHostName(Enum):
    STARRYDATA2 = "starrydata2"
    CLEANSING_DATASET = "cleansing_dataset"

class GraphRepositoryFactory:
    @staticmethod
    def create(api_host_name: ApiHostName) -> GraphRepository:
        if api_host_name.value == ApiHostName.STARRYDATA2.value:
            return GraphRepositoryApiStarrydata2()
        elif api_host_name.value == ApiHostName.CLEANSING_DATASET.value:
            return GraphRepositoryApiCleansingDataset()
        else:
            raise ValueError(f"Unknown api_: {api_host_name}")
