"""Filesystem paths used by the framework."""

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]  # src/eli_lab
PACKAGE_ASSETS_ROOT = PACKAGE_ROOT / "assets"
BLENDER_TEMPLATES_ROOT = PACKAGE_ASSETS_ROOT / "blender" / "templates"


def blender_template(name: str) -> Path:
    """Return the path to a packaged Blender template."""
    return BLENDER_TEMPLATES_ROOT / name
