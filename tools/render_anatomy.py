"""Generate static fallback images from the same local meshes (development only).

Run from repository root: .venv/bin/python -m tools.render_anatomy
Requires requirements-dev.txt and Chromium; set CHROMIUM_PATH if necessary.
"""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
from healthrisk.visuals import anatomy_figure, fallback_path, MODEL_KEYS

with sync_playwright() as playwright, TemporaryDirectory() as temp:
    browser = playwright.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'), headless=True,
        args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page = browser.new_page(viewport={'width':850,'height':700}, device_scale_factor=1)
    for organ in MODEL_KEYS:
        fig = anatomy_figure(organ, comparison=False)
        html = Path(temp)/'model.html'
        html.write_text(fig.to_html(include_plotlyjs=True,config={'displayModeBar':False},default_width='100%',default_height='650px'))
        page.set_content(html.read_text(), timeout=60000)
        page.wait_for_selector('.gl-container canvas')
        page.wait_for_function("document.querySelector('.js-plotly-plot')._fullLayout.scene._scene.glplot != null")
        page.wait_for_timeout(1800)
        page.locator('.js-plotly-plot').screenshot(path=str(fallback_path(organ)))
        print('Rendered',organ,flush=True)
    browser.close()
