"""Filesystem paths used by the framework.

All repository-relative resources are resolved from this module instead of
assuming a developer-specific working directory.
"""

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]        # src/eli_lab
# /src/eli_lab/core/paths.py -> parents[3] is the repository root.
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ASSETS_ROOT = REPOSITORY_ROOT / "assets"
BLENDER_TEMPLATES_ROOT = ASSETS_ROOT / "blender" / "templates"


def blender_template(name: str) -> Path:
    """Return the path to a bundled Blender template."""
    return BLENDER_TEMPLATES_ROOT / name
