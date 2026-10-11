"""Real-browser regression checks. Run with a local Streamlit server active.

.venv/bin/python -m tools.browser_smoke --url http://127.0.0.1:8502
Requires requirements-dev.txt and Chromium (CHROMIUM_PATH override supported).
"""
import argparse
import os
import json
import numpy as np
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
from healthrisk.visuals import MODEL_KEYS
from healthrisk.data import generate_data

parser = argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8502')
args = parser.parse_args()
with sync_playwright() as playwright, TemporaryDirectory() as temp:
    browser = playwright.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,
        args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page = browser.new_page(viewport={'width':1440,'height':1100})
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.goto(args.url)
    page.get_by_text('anatomical explorer',exact=False).wait_for(timeout=60000)
    for organ in MODEL_KEYS:
        page.get_by_test_id('stRadio').get_by_text(organ,exact=True).click()
        page.get_by_role('heading',name=f'{organ} · anatomical explorer',exact=True).wait_for()
        viewer=page.locator('.js-plotly-plot').filter(has=page.locator('.gl-container')).first
        page.wait_for_function("organ => { const p=[...document.querySelectorAll('.js-plotly-plot')].find(p=>p._fullLayout?.scene2); return p && p._fullLayout.meta.organ===organ && p._fullLayout.scene._scene?.glplot && p._fullLayout.scene2._scene?.glplot; }", arg=organ)
        page.wait_for_timeout(500)
        viewer.scroll_into_view_if_needed()
        camera="el => JSON.stringify(el._fullLayout.scene._scene.getCamera())"
        before=viewer.evaluate(camera)
        right_before=viewer.evaluate("el => JSON.stringify(el._fullLayout.scene2._scene.getCamera())")
        box=viewer.bounding_box()
        x,y=box['x']+box['width']*.22,box['y']+box['height']*.5
        page.mouse.move(x,y)
        page.mouse.down()
        page.mouse.move(x+65,y+30,steps=12)
        page.mouse.up()
        page.wait_for_timeout(400)
        after=viewer.evaluate(camera)
        assert before!=after, f'{organ}: mouse rotation did not change camera'
        page.mouse.move(x,y)
        page.mouse.wheel(0,-300)
        page.wait_for_timeout(400)
        assert viewer.evaluate(camera)!=after, f'{organ}: wheel zoom did not change camera'
        assert viewer.evaluate("el => JSON.stringify(el._fullLayout.scene2._scene.getCamera())")==right_before, f'{organ}: second camera unexpectedly changed'
        zoomed=viewer.evaluate(camera)
        viewer.locator('[data-title="Reset camera to last save"]').click()
        page.wait_for_timeout(400)
        reset=viewer.evaluate(camera)
        assert reset!=zoomed, f'{organ}: camera reset did not change camera'
        for field in ['eye','center','up']:
            np.testing.assert_allclose(list(json.loads(reset)[field].values()),list(json.loads(before)[field].values()),atol=1e-5)
        # Ensure both identical panels have actual rendered canvas content.
        assert viewer.locator('canvas').count()>=2
        print('PASS rotation + zoom:',organ,flush=True)
    page.get_by_text('Use static anatomical rendering (no WebGL)',exact=True).click()
    page.locator('[data-testid="stImage"]').first.wait_for()
    assert page.locator('[data-testid="stImage"]').count()==2
    assert page.locator('[data-testid="stImage"] img').evaluate_all('(images)=>images.every(img=>img.complete && img.naturalWidth>0)')
    page.get_by_text('Use static anatomical rendering (no WebGL)',exact=True).click()
    # Test a real upload and its explicit synthetic-only confirmation.
    sample=Path(temp)/'synthetic.csv'
    generate_data(12).to_csv(sample,index=False)
    page.locator('input[type=file]').set_input_files(str(sample))
    page.get_by_text('I confirm the uploaded file contains synthetic data only',exact=True).click()
    page.get_by_text('Validated 12 synthetic records.',exact=False).wait_for(timeout=30000)
    with page.expect_download() as download:
        page.get_by_role('button',name='↓ Filtered synthetic records · CSV').click()
    exported=Path(temp)/'export.csv'
    download.value.save_as(exported)
    import pandas as pd
    assert len(pd.read_csv(exported))==12
    with page.expect_download() as download:
        page.get_by_role('button',name='↓ Summary report · Markdown').click()
    report=Path(temp)/'report.md'
    download.value.save_as(report)
    assert 'Records: 12' in report.read_text()
    assert not errors, errors
    page.set_viewport_size({'width':390,'height':844})
    page.get_by_role('heading',name='HealthRisk',exact=True).wait_for()
    page.screenshot(path='/tmp/healthrisk-mobile.png',full_page=True)
    print('PASS fallback, upload, CSV download, report download, narrow viewport; no JavaScript errors',flush=True)
    browser.close()
