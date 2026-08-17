"""Filesystem paths used by the framework."""

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PACKAGE_ROOT.parent.parent
REPOSITORY_ROOT = SOURCE_ROOT.parent
ASSETS_ROOT = REPOSITORY_ROOT / "assets"
BLENDER_TEMPLATES_ROOT = ASSETS_ROOT / "blender" / "templates"


def blender_template(name: str) -> Path:
    """Return the path to a bundled Blender template."""
    return BLENDER_TEMPLATES_ROOT / name
