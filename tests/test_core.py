from pathlib import Path

from eli_lab.core.config import DEFAULT_CONFIG
from eli_lab.core.paths import BLENDER_TEMPLATES_ROOT, blender_template


def test_default_config_uses_shared_template_root():
    assert DEFAULT_CONFIG.blender_templates_root == BLENDER_TEMPLATES_ROOT


def test_blender_template_returns_path():
    path = blender_template("Asset.blend")
    assert isinstance(path, Path)
    assert path.name == "Asset.blend"
