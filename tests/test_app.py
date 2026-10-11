from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / 'app.py')


def test_dashboard_default_organs_and_filters():
    app = AppTest.from_file(APP).run(timeout=30)
    assert not app.exception
    assert app.metric[0].value == '2,500'
    for organ in ['Heart','Lungs','Kidneys','Liver','Whole body']:
        app.radio[0].set_value(organ).run(timeout=30)
        assert not app.exception
        assert any(organ in s.value for s in app.subheader)
    app.slider[0].set_value((40,60)).run(timeout=30)
    assert not app.exception
    assert 0 < int(app.metric[0].value.replace(',','')) < 2500
    app.multiselect[0].set_value([]).run(timeout=30)
    assert not app.exception
    assert app.metric[0].value == '0'
    assert any('No records' in w.value for w in app.warning)


def test_uploaded_dataset_and_invalid_fallback():
    import io
    from unittest.mock import patch
    from healthrisk.data import generate_data
    payload = io.BytesIO(generate_data(12).to_csv(index=False).encode())
    with patch('streamlit.file_uploader', return_value=payload):
        app = AppTest.from_file(APP).run(timeout=30)
        assert app.metric[0].value == '2,500'
        app.checkbox[0].set_value(True).run(timeout=30)
        assert not app.exception
        assert app.metric[0].value == '12'
        assert any('Validated 12' in item.value for item in app.success)
    with patch('streamlit.file_uploader', return_value=io.BytesIO(b'age\nwrong')):
        app = AppTest.from_file(APP).run(timeout=30)
        app.checkbox[0].set_value(True).run(timeout=30)
        assert not app.exception
        assert app.metric[0].value == '2,500'
        assert any('Missing required columns' in item.value for item in app.error)
        assert any('Upload was rejected' in item.value for item in app.warning)


def test_static_fallback_all_organs_and_analytics():
    app = AppTest.from_file(APP).run(timeout=30)
    app.toggle[0].set_value(True).run(timeout=30)
    for organ in ['Heart','Lungs','Kidneys','Liver','Whole body']:
        app.radio[0].set_value(organ).run(timeout=30)
        assert not app.exception
        assert len(app.get('imgs')) == 2
        assert app.metric[0].value == '2,500'
        assert len(app.get('plotly_chart')) == 4
    app.toggle[0].set_value(False).run(timeout=30)
    assert not app.exception
    assert len(app.get('plotly_chart')) == 5
