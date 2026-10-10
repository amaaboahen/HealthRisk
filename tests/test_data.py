import numpy as np
import pandas as pd
import pytest
from healthrisk.data import generate_data, score_data, validate_data, filter_data, REQUIRED, ORGANS
from healthrisk.analytics import insights, summary_report


def test_reproducible_sample_and_schema():
    df = generate_data()
    pd.testing.assert_frame_equal(df, generate_data())
    assert len(df) == 2500
    assert df.patient_id.is_unique
    checked, errors = validate_data(df)
    assert not errors
    pd.testing.assert_frame_equal(df, checked)
    assert not df.equals(generate_data(seed=1))
    for organ in ORGANS:
        key = organ.lower().replace(' ', '_')
        assert df[f'{key}_score'].between(0,100).all()
        assert set(df[f'{key}_risk']) == {'Lower', 'Moderate', 'Higher'}


@pytest.mark.parametrize('column,value,message', [
    ('age', np.inf, 'finite'), ('age', 18.5, 'whole years'),
    ('sex', 'invalid', 'sex must'), ('bmi', None, 'bmi must'),
    ('smoking_status', 'unknown', 'smoking_status must'),
    ('smoking_duration', 73, 'smoking_duration'),
    ('patient_id', '', 'patient_id'),
    ('diastolic_bp', 150, 'below systolic')])
def test_invalid_upload(column, value, message):
    df = generate_data(5)[REQUIRED].copy()
    df[column] = df[column].astype(object)
    df.loc[0,column] = value
    result, errors = validate_data(df)
    assert result is None
    assert any(message in e for e in errors)


def test_upload_missing_duplicate_and_recomputed_scores():
    df = generate_data(10)
    assert validate_data(df.drop(columns=['age']))[0] is None
    df.loc[1,'patient_id'] = df.loc[0,'patient_id']
    assert validate_data(df)[0] is None
    df = generate_data(10)
    df['heart_score'] = -99
    clean, errors = validate_data(df)
    assert not errors and clean.heart_score.ge(0).all()
    assert validate_data(df.iloc[:0])[0] is None


def test_never_smoker_and_onset_constraints():
    df = generate_data(5)
    df.loc[0, ['age', 'smoking_status', 'smoking_duration']] = [20, 'Never', 3]
    assert len(validate_data(df)[1]) == 2


def test_score_thresholds_and_weights():
    # Equal normalized inputs make all organ scores equal, independently of weights.
    df = pd.DataFrame({'age':[18+72*x for x in [0,.35,.6,1]],
        'smoking_duration':[60*x for x in [0,.35,.6,1]],
        'bmi':[18+22*x for x in [0,.35,.6,1]],
        'cholesterol':[120+180*x for x in [0,.35,.6,1]],
        'systolic_bp':[90+90*x for x in [0,.35,.6,1]]})
    out = score_data(df)
    for organ, weights in ORGANS.items():
        assert sum(weights.values()) == pytest.approx(1)
        key = organ.lower().replace(' ','_')
        assert out[f'{key}_risk'].tolist() == ['Lower','Lower','Moderate','Higher']
        assert out[f'{key}_score'].tolist() == [0,35,60,100]


def test_filters_insights_and_report():
    df = generate_data()
    subset = filter_data(df, (40,60), ['Never'], ['Female'], (20,30))
    assert len(subset) > 0
    assert subset.age.between(40,60).all()
    assert subset.smoking_status.eq('Never').all()
    assert subset.sex.eq('Female').all()
    assert subset.bmi.between(20,30).all()
    assert 'not causal evidence' in ' '.join(insights(df,'Heart'))
    report = summary_report(subset,'Heart','test','age 40–60')
    assert f'Records: {len(subset):,}' in report
    assert 'not diagnoses' in report
    empty = filter_data(df,(18,90),[],[],(12,60))
    assert empty.empty and 'No records' in insights(empty,'Heart')[0]
    assert 'Records: 0' in summary_report(empty,'Heart','test','empty')
