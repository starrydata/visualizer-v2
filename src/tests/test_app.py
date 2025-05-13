import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, Mock
from bokeh.models import ColumnDataSource
import app as app

# モック用のJSONレスポンスデータ
mock_json_response = {
    "data": {
        "x": [[i + j * 0.1 for i in range(10)] for j in range(10)],
        "y": [[i * 2 + j * 0.2 for i in range(10)] for j in range(10)],
        "SID": [str(100 + j) for j in range(10)],
    },
    "prop_x": "X Axis",
    "prop_y": "Y Axis",
    "unit_x": "units",
    "unit_y": "units",
}


@patch("app.requests.get")
def test_make_source(mock_get):
    # requests.getのモック設定
    mock_resp = Mock()
    mock_resp.json.return_value = mock_json_response
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    source, content = app.make_source("dummy_url")

    # ColumnDataSourceの型チェック
    assert isinstance(source, ColumnDataSource)

    # contentがモックのJSONと一致するか
    assert content == mock_json_response

    # sourceのデータが正しくフラット化されているか
    data = source.data
    expected_x = []
    expected_y = []
    expected_sid = []
    for j in range(10):
        for i in range(10):
            expected_x.append(i + j * 0.1)
            expected_y.append(i * 2 + j * 0.2)
            expected_sid.append(100 + j)
    assert data["x"] == expected_x
    assert data["y"] == expected_y
    assert data["SID"] == expected_sid


import json


@patch("app.generate_graph")
@patch("app.generate_slideshow")
def test_generate_slideshow(mock_generate_slideshow, mock_generate_graph):
    # generate_graphのモック設定
    mock_generate_graph.side_effect = [
        ("<div>graph1</div>", "<script>script1</script>", "Title1"),
        ("<div>graph2</div>", "<script>script2</script>", "Title2"),
    ]

    # generate_slideshowのモック設定
    mock_generate_slideshow.return_value = ("./dist/test.html", "<html>test</html>")

    # 実際の呼び出し
    graphs = []
    for i in range(2):
        div, script, title = mock_generate_graph(
            f"url{i}", f"hl{i}", "linear", [0, 1], [0, 1]
        )
        graphs.append((div, script, title))
    out_path, html_content = mock_generate_slideshow(graphs)

    # 呼び出し回数の検証
    assert mock_generate_graph.call_count == 2
    mock_generate_slideshow.assert_called_once_with(graphs)

    # 戻り値の検証
    assert out_path == "./dist/test.html"
    assert html_content == "<html>test</html>"
