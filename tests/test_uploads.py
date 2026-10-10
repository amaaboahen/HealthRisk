from healthrisk.data import generate_data, REQUIRED
from healthrisk.uploads import load_csv


def test_csv_roundtrip_preserves_ids_and_recomputes():
    df = generate_data(10)
    df['patient_id'] = [f'{i:04d}' for i in range(10)]
    df['heart_score'] = 999
    result, errors = load_csv(df.to_csv(index=False).encode())
    assert not errors
    assert result.patient_id.tolist() == df.patient_id.tolist()
    assert result.heart_score.le(100).all()


def test_bad_csv_boundaries():
    for payload in [b'', b'age,age\n20,21', b'age,sex\n20,Male,extra', b'age,sex\n20', b'\xff\xfe', b'x'*(10*1024*1024+1)]:
        result, errors = load_csv(payload)
        assert result is None and errors


def test_sample_file_is_current():
    from pathlib import Path
    result, errors = load_csv((Path(__file__).resolve().parents[1] / 'data/synthetic_patients.csv').read_bytes())
    assert not errors
    import pandas as pd
    pd.testing.assert_frame_equal(result, generate_data())
