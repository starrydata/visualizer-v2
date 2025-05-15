import pytest
from application.services import GraphGenerationService, SlideshowGenerationService, load_js_code
from domain.slideshow import Slideshow
from unittest.mock import patch, Mock
from bokeh.plotting import Figure

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

    # モックのファイルオブジェクトを設定
    mock_file = Mock()
    mock_open.return_value.__enter__.return_value.read.return_value = """
    <html>
    <body>Mock Template Content</body>
    </html>
    """

    # テンプレートファイルの読み込みもモック化
    with patch("builtins.open", mock_open):
        out_path, html = service.generate_slideshow(graphs)

    assert out_path == "./dist/starrydata_slideshow.html"
    assert isinstance(html, str)
    assert isinstance(out_path, str)
