from typing import List, Tuple

class Slideshow:
    def __init__(self, graphs: List[Tuple[str, str, str]]):
        # graphs は (div, script, title) のタプルのリスト
        self.graphs = graphs

    def add_graph(self, div: str, script: str, title: str):
        self.graphs.append((div, script, title))

    def get_titles(self) -> List[str]:
        return [title for _, _, title in self.graphs]

    def get_html_fragments(self) -> List[str]:
        return [div + script for div, script, _ in self.graphs]
