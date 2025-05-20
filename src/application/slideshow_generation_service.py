import os

from domain.slideshow import Slideshow

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict

from bokeh.resources import CDN



class SlideshowGenerationService:
    def __init__(self, template_path: str = "src/templates/starrydata_slideshow.html"):
        self.template_path = template_path

    def generate_slideshow(self, graphs: Slideshow, material_type: str = "starrydata") -> Tuple[str, str]:
        divs = [div for div, _, _ in graphs.graphs]
        scripts = [script for _, script, _ in graphs.graphs]
        titles = graphs.get_titles()

        menu_items = "".join(
            [f'<li id="menu{idx}">{title}</li>' for idx, title in enumerate(titles)]
        )

        plots_html = "".join(
            [
                f'<div id="plot{idx}" class="plot-container">{divs[idx]}{scripts[idx]}</div>'
                for idx in range(len(divs))
            ]
        )

        with open(self.template_path, "r", encoding="utf-8") as f:
            template = f.read()

        html = (
            template.replace("{{ menu_items|safe }}", menu_items)
            .replace("{{ plots_html|safe }}", plots_html)
            .replace("{{ bokeh_cdn }}", CDN.render())
        )

        safe_material_type = material_type.replace(" ", "_").lower()
        out = f"./dist/{safe_material_type}_slideshow.html"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated: {out}")
        return out, html

