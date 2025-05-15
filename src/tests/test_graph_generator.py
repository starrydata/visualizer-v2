import pytest
from domain.graph import Graph, GraphDataPoint
from domain.slideshow import Slideshow
from application.services import GraphGenerationService, SlideshowGenerationService, load_js_code
from unittest.mock import patch, Mock
from bokeh.plotting import Figure

def test_graph_data_point():
    dp = GraphDataPoint(1.0, 2.0, 100)
    assert dp.x == 1.0
    assert dp.y == 2.0
    assert dp.sid == 100

def test_graph_validation():
    graph = Graph(
        prop_x="X",
        prop_y="Y",
        unit_x="units",
        unit_y="units",
        data_points=[GraphDataPoint(1, 2, 3)],
        y_scale="linear",
        x_range=[0, 10],
        y_range=[0, 10],
    )
    assert graph.validate() is True

    empty_graph = Graph(
        prop_x="X",
        prop_y="Y",
        unit_x="units",
        unit_y="units",
        data_points=[],
        y_scale="linear",
        x_range=[0, 10],
        y_range=[0, 10],
    )
    assert empty_graph.validate() is False

def test_slideshow_add_and_getters():
    slideshow = Slideshow([])
    slideshow.add_graph("<div>", "<script>", "Title1")
    slideshow.add_graph("<div2>", "<script2>", "Title2")

    titles = slideshow.get_titles()
    assert titles == ["Title1", "Title2"]

    html_fragments = slideshow.get_html_fragments()
    assert html_fragments == ["<div><script>", "<div2><script2>"]

@patch("application.services.requests.get")
def test_graph_generation_service_create_graph(mock_get):
    scatter_js, line_js, label_js = load_js_code()
    service = GraphGenerationService(scatter_js, line_js, label_js)

    mock_response = Mock()
    mock_response.json.return_value = {
        "prop_x": "X Axis",
        "prop_y": "Y Axis",
        "unit_x": "units",
        "unit_y": "units",
        "data": {
            "x": [[1, 2], [3, 4]],
            "y": [[5, 6], [7, 8]],
            "SID": ["100", "101"]
        }
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    div, script, title, figure = service.create_graph(
        "http://dummy_json_path",
        "http://dummy_highlight_path",
        "linear",
        [0, 10],
        [0, 10]
    )

    assert "X Axis" in div or "Y Axis" in div or title == "Y Axis"
    assert isinstance(div, str)
    assert isinstance(script, str)
    assert isinstance(title, str)
    assert isinstance(figure, Figure)

@patch("application.services.open", create=True)
@patch("application.services.os.makedirs")
def test_slideshow_generation_service_generate_slideshow(mock_makedirs, mock_open):
    service = SlideshowGenerationService(template_path="src/templates/starrydata_slideshow.html")

    graphs = Slideshow([
        ("<div1>", "<script1>", "Title1"),
        ("<div2>", "<script2>", "Title2"),
    ])

    # モックのファイルオブジェクトを設定し、read()が文字列を返すようにする
    mock_file = Mock()
    mock_file.read.return_value = """
    <html>
    <body>Mock Template Content</body>
    </html>
    """
    mock_open.return_value.__enter__.return_value = mock_file

    out_path, html = service.generate_slideshow(graphs)

    assert out_path == "./dist/starrydata_slideshow.html"
    # htmlは文字列であることを確認
    assert isinstance(html, str)
