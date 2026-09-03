"""Blender template provisioning services."""

from __future__ import annotations

import shutil
from pathlib import Path

from eli_lab.core.paths import blender_template

TEMPLATE_FILES = {
    "characters": "Character.blend",
    "locations": "Location.blend",
    "models": "Asset.blend",
}


def provision_blender_file(
    directory: str | Path, category: str, *, overwrite: bool = False
) -> Path | None:
    """Copy the template for *category* into a leaf asset directory."""
    target_dir = Path(directory).expanduser().resolve()
    if not target_dir.is_dir():
        raise NotADirectoryError(target_dir)
    try:
        template = blender_template(TEMPLATE_FILES[category])
    except KeyError as exc:
        raise ValueError(f"unknown Blender template category: {category}") from exc
    if not template.is_file():
        raise FileNotFoundError(template)

    output = target_dir / f"{target_dir.name.lower().replace(' ', '_')}.blend"
    if output.exists() and not overwrite:
        return None
    shutil.copy2(template, output)
    return output
