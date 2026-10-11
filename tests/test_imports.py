"""Fresh-process and stale-module deployment import regressions."""
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


def run_python(code):
    result = subprocess.run([sys.executable, '-c', code],cwd=ROOT,capture_output=True,text=True,timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'IMPORT_OK' in result.stdout


def test_app_imports_in_a_fresh_process():
    # Actual Python import, not a syntax check or import of only helper functions.
    run_python("import app; assert app.condition in app.CONDITIONS; print('IMPORT_OK')")


def test_app_imports_with_pre_condition_visuals_cached():
    run_python('''
import sys, types
import healthrisk
legacy = types.ModuleType('healthrisk.visuals')
legacy.__package__ = 'healthrisk'
legacy.__file__ = 'cached-pre-condition-release/healthrisk/visuals.py'
legacy.MODEL_KEYS = {'Kidneys': 'kidneys'}
legacy.anatomy_figure = lambda *args, **kwargs: None
legacy.fallback_path = lambda *args, **kwargs: None
sys.modules['healthrisk.visuals'] = legacy
assert not hasattr(legacy, 'condition_figure')
import app
assert app.condition_figure(app.condition).layout.images[0].source != app.condition_figure(app.condition).layout.images[1].source
assert 'Kidneys' not in app.MODEL_KEYS
assert sys.modules['healthrisk.visuals'] is legacy
print('IMPORT_OK')
''')


@pytest.mark.parametrize('first', ['healthrisk.anatomy_views','healthrisk.condition_views'])
def test_view_import_order_and_compatibility_exports(first):
    run_python(f'''
import importlib
importlib.import_module({first!r})
from healthrisk import visuals
from healthrisk.anatomy_views import anatomy_figure, MODEL_KEYS
from healthrisk.condition_views import condition_figure
assert visuals.anatomy_figure is anatomy_figure
assert visuals.condition_figure is condition_figure
assert visuals.MODEL_KEYS is MODEL_KEYS
assert callable(visuals.fallback_path)
print('IMPORT_OK')
''')
