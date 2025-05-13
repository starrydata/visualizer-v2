import pytest
from domain.slideshow import Slideshow

def test_slideshow_add_and_getters():
    slideshow = Slideshow([])
    slideshow.add_graph("<div>", "<script>", "Title1")
    slideshow.add_graph("<div2>", "<script2>", "Title2")

    titles = slideshow.get_titles()
    assert titles == ["Title1", "Title2"]

    html_fragments = slideshow.get_html_fragments()
    assert html_fragments == ["<div><script>", "<div2><script2>"]
