from pathlib import Path
import numpy as np
import pytest
from healthrisk.visuals import load_model, anatomy_figure, fallback_path, MODEL_KEYS


@pytest.mark.parametrize('organ', list(MODEL_KEYS))
def test_local_mesh_integrity_and_identical_comparisons(organ):
    model = load_model(organ)
    assert model['source_commit'] == '9de5d6912a1b0df9cab739d57f00e036b0496ddc'
    for part in model['parts']:
        vertices, faces = np.array(part['vertices']), np.array(part['faces'])
        assert vertices.ndim == faces.ndim == 2
        assert vertices.shape[1] == faces.shape[1] == 3
        assert np.isfinite(vertices).all()
        assert faces.min() >= 0 and faces.max() < len(vertices)
        assert len(faces) > 100
    fig = anatomy_figure(organ)
    count = len(model['parts'])
    assert len(fig.data) == count*2
    for lower, higher in zip(fig.data[:count], fig.data[count:]):
        for axis in ['x','y','z','i','j','k']:
            np.testing.assert_array_equal(getattr(lower,axis),getattr(higher,axis))
        assert lower.color == higher.color
    assert fig.layout.scene.dragmode == fig.layout.scene2.dragmode == 'orbit'
    assert fig.layout.scene.camera == fig.layout.scene2.camera
    assert fig.layout.uirevision == f'anatomy-{organ}'
    assert fallback_path(organ).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')


def test_anatomy_is_independent_of_risk_data():
    from inspect import signature
    assert list(signature(anatomy_figure).parameters) == ['organ','comparison']
    assert sum(len(p['faces']) for p in load_model('Whole body')['parts']) < 160000
