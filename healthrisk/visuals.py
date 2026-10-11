"""Compatibility exports for existing tools; the app uses explicit view modules.

Separating condition and anatomy views avoids requiring a newly added symbol
from an older ``healthrisk.visuals`` module retained by a running deployment.
"""
from .anatomy_views import (
    ASSET_DIR, CAMERA, MODEL_KEYS, anatomy_figure, fallback_path, load_model,
)
from .condition_views import condition_figure

__all__ = [
    "ASSET_DIR", "CAMERA", "MODEL_KEYS", "anatomy_figure", "fallback_path",
    "load_model", "condition_figure",
]
