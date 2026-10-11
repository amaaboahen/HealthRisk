"""Actual browser checks; run with the local Streamlit server active.

.venv/bin/python -m tools.browser_smoke --url http://127.0.0.1:8502
Requires development Playwright and Chromium (CHROMIUM_PATH override supported).
"""
import argparse
import os
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
from healthrisk.education import CONDITIONS, condition_options
from healthrisk.visuals import MODEL_KEYS
from healthrisk.data import generate_data

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8502')
args=parser.parse_args()
with sync_playwright() as playwright, TemporaryDirectory() as temp:
    browser=playwright.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,
        args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1100})
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.goto(args.url)
    page.get_by_role('heading',name='Whole body · condition explorer',exact=True).wait_for(timeout=60000)
    for organ in ['Heart','Lungs','Kidneys','Liver','Whole body']:
        page.get_by_test_id('stRadio').get_by_text(organ,exact=True).click()
        page.get_by_role('heading',name=f'{organ} · condition explorer',exact=True).wait_for()
        condition=condition_options(organ)[0]
        page.wait_for_function("condition => [...document.querySelectorAll('.js-plotly-plot')].some(p=>p._fullLayout?.meta?.condition===condition)",arg=condition)
        viewer=page.get_by_test_id('stPlotlyChart').first.locator('.js-plotly-plot')
        page.wait_for_timeout(300)
        viewer.scroll_into_view_if_needed()
        before=viewer.evaluate('el => JSON.stringify(el._fullLayout.xaxis.range)')
        right_before=viewer.evaluate('el => JSON.stringify(el._fullLayout.xaxis2.range)')
        box=viewer.bounding_box()
        x,y=box['x']+box['width']*.23,box['y']+box['height']*.5
        page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+60,y+25,steps=8);page.mouse.up()
        page.wait_for_timeout(300)
        after=viewer.evaluate('el => JSON.stringify(el._fullLayout.xaxis.range)')
        assert before!=after, f'{organ}: image pan failed'
        page.mouse.move(x,y);page.mouse.wheel(0,-250)
        page.wait_for_timeout(400)
        assert after!=viewer.evaluate('el => JSON.stringify(el._fullLayout.xaxis.range)'), f'{organ}: image zoom failed'
        assert right_before==viewer.evaluate('el => JSON.stringify(el._fullLayout.xaxis2.range)'), f'{organ}: panels are coupled'
        assert viewer.evaluate('el => el._fullLayout.images[0].source!==el._fullLayout.images[1].source')
        print('PASS independent condition illustration pan/zoom:',organ,flush=True)
        details=page.locator('details').filter(has_text='3D reference anatomy & licensed source illustrations')
        if not details.evaluate('el => el.open'):
            details.locator('summary').click()
        if organ in MODEL_KEYS:
            reference=details.locator('.js-plotly-plot')
            reference.scroll_into_view_if_needed()
            page.wait_for_function("organ => [...document.querySelectorAll('.js-plotly-plot')].some(p=>p._fullLayout?.meta?.organ===organ && p._fullLayout.scene?._scene?.glplot)",arg=organ)
            camera='el => JSON.stringify(el._fullLayout.scene._scene.getCamera())'
            initial=reference.evaluate(camera)
            box=reference.bounding_box()
            x,y=box['x']+box['width']*.5,box['y']+box['height']*.5
            page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+65,y+30,steps=8);page.mouse.up()
            page.wait_for_timeout(300)
            rotated=reference.evaluate(camera)
            assert initial!=rotated,f'{organ}: reference rotation failed'
            page.mouse.wheel(0,-250);page.wait_for_timeout(400)
            assert reference.evaluate(camera)!=rotated,f'{organ}: reference zoom failed'
            print('PASS reference 3D rotate/zoom:',organ,flush=True)
        else:
            assert details.locator('img').count()>=1
        details.locator('summary').click()
    # Whole-body topic selection should not alter its analytics population.
    metrics=page.get_by_test_id('stMetricValue')
    baseline=metrics.first.inner_text()
    selector=page.get_by_test_id('stSelectbox').first
    for condition in CONDITIONS:
        selector.locator('[role=combobox]').click()
        page.get_by_role('option',name=condition,exact=True).click()
        page.wait_for_function("condition => [...document.querySelectorAll('.js-plotly-plot')].some(p=>p._fullLayout?.meta?.condition===condition)",arg=condition)
        assert metrics.first.inner_text()==baseline
    page.get_by_text('Use static educational illustrations (no interactive canvas)',exact=True).click()
    page.get_by_test_id('stImage').first.wait_for()
    assert page.get_by_test_id('stImage').count()>=2
    page.get_by_text('Use static educational illustrations (no interactive canvas)',exact=True).click()
    sample=Path(temp)/'synthetic.csv';generate_data(12).to_csv(sample,index=False)
    page.locator('input[type=file]').set_input_files(str(sample))
    page.get_by_text('I confirm the uploaded file contains synthetic data only',exact=True).click()
    page.get_by_text('Validated 12 synthetic records.',exact=False).wait_for(timeout=30000)
    with page.expect_download() as download:
        page.get_by_role('button',name='↓ Filtered synthetic records · CSV').click()
    exported=Path(temp)/'data.csv';download.value.save_as(exported)
    import pandas as pd
    assert len(pd.read_csv(exported))==12
    with page.expect_download() as download:
        page.get_by_role('button',name='↓ Summary report · Markdown').click()
    report=Path(temp)/'report.md';download.value.save_as(report)
    assert 'Records: 12' in report.read_text()
    assert 'Independently selected educational topic' in report.read_text()
    assert not errors,errors
    page.set_viewport_size({'width':390,'height':844})
    page.get_by_role('heading',name='HealthRisk',exact=True).wait_for()
    page.screenshot(path='/tmp/healthrisk-condition-mobile.png',full_page=True)
    print('PASS condition selection independence, static fallback, upload, CSV/report downloads, narrow viewport; no JavaScript errors',flush=True)
    browser.close()
