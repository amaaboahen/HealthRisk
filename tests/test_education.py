import numpy as np
import pytest
from streamlit.testing.v1 import AppTest
from pathlib import Path
from healthrisk.education import CONDITIONS, condition_options, cohort_context, illustration_path
from healthrisk.visuals import condition_figure, MODEL_KEYS
from healthrisk.data import generate_data, filter_data
from healthrisk.analytics import summary_report

APP = str(Path(__file__).resolve().parents[1]/'app.py')


@pytest.mark.parametrize('organ',['Heart','Lungs','Kidneys','Liver','Whole body'])
def test_condition_comparisons(organ):
    options=condition_options(organ)
    assert options
    for condition in options:
        ref, affected=illustration_path(condition), illustration_path(condition,True)
        assert ref.read_bytes().startswith(b'\x89PNG')
        assert affected.read_bytes().startswith(b'\x89PNG')
        assert ref.read_bytes()!=affected.read_bytes()
        fig=condition_figure(condition)
        assert fig.layout.images[0].source!=fig.layout.images[1].source
        assert fig.layout.dragmode=='pan'
        assert fig.layout.meta['population_independent']
        assert fig.layout.xaxis.matches is None and fig.layout.xaxis2.matches is None
        assert CONDITIONS[condition]['sources']


def test_cohort_filters_change_context_not_artwork():
    full=generate_data()
    condition='Emphysema'
    figure=condition_figure(condition).to_json()
    subset=filter_data(full,(40,65),['Former'],['Female'],(20,30))
    assert len(subset)>0
    assert cohort_context(full,condition)!=cohort_context(subset,condition)
    assert f'{len(subset):,} synthetic records' in cohort_context(subset,condition)
    assert condition_figure(condition).to_json()==figure
    assert 'No synthetic records' in cohort_context(subset.iloc[:0],condition)
    report=summary_report(subset,'Lungs','test','filters',condition=condition)
    assert 'Independently selected educational topic' in report
    assert 'not inferred organ damage' in report
    assert 'Emphysema' in report


def test_restricted_kidney_artwork_removed():
    assert 'Kidneys' not in MODEL_KEYS
    root=Path(APP).parent/'assets'/'anatomy'
    assert not (root/'kidneys.json.gz').exists()
    assert not (root/'kidneys.png').exists()
    assert (Path(APP).parent/'assets'/'education'/'kidney_reference.jpg').exists()


def test_all_filter_widgets_recalculate_and_keep_condition():
    app=AppTest.from_file(APP).run(timeout=30)
    app.radio[0].set_value('Lungs').run(timeout=30)
    initial_context=' '.join(m.value for m in app.markdown)
    app.multiselect[0].set_value(['Current']).run(timeout=30)
    app.multiselect[1].set_value(['Male']).run(timeout=30)
    app.slider[0].set_value((40,65)).run(timeout=30)
    app.slider[1].set_value((20.,30.)).run(timeout=30)
    expected=filter_data(generate_data(),(40,65),['Current'],['Male'],(20.,30.))
    assert app.metric[0].value==f'{len(expected):,}'
    assert app.metric[1].value==f'{expected.lungs_score.mean():.1f} / 100'
    assert app.metric[2].value==f"{expected.lungs_risk.eq('Higher').mean():.1%}"
    assert app.selectbox[0].value=='Emphysema'
    assert not app.exception
    updated=' '.join(m.value for m in app.markdown)
    assert initial_context!=updated
    assert 'condition prevalence' in updated
    app.multiselect[1].set_value(['Female']).run(timeout=30)
    expected=filter_data(generate_data(),(40,65),['Current'],['Female'],(20.,30.))
    assert app.metric[0].value==f'{len(expected):,}'


def test_whole_body_condition_selection_does_not_relabel_population():
    app=AppTest.from_file(APP).run(timeout=30)
    baseline=[metric.value for metric in app.metric[:4]]
    for condition in CONDITIONS:
        app.selectbox[0].set_value(condition).run(timeout=30)
        assert not app.exception
        assert [metric.value for metric in app.metric[:4]]==baseline
        assert any(CONDITIONS[condition]['visible'] in m.value for m in app.markdown)
