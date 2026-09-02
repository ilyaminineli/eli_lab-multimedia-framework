"""Safe texture relocation with Blender reference repair."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


RELOCATE_SCRIPT = r'''
import bpy
import os
import sys

old_path = os.path.abspath(sys.argv[-2])
new_path = os.path.abspath(sys.argv[-1])
old_norm = os.path.normcase(old_path)

changed = False
for image in bpy.data.images:
    if image.source != 'FILE' or not image.filepath:
        continue
    absolute = os.path.abspath(bpy.path.abspath(image.filepath))
    if os.path.normcase(absolute) == old_norm:
        image.filepath = bpy.path.relpath(new_path)
        image.filepath_raw = bpy.path.relpath(new_path)
        changed = True

if changed:
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('ELI_LAB_RELOCATED=' + ('1' if changed else '0'))
'''


def repair_blend_texture_reference(blend_file: str | Path, old_path: str | Path, new_path: str | Path, blender_executable: str) -> bool:
    """Rewrite an image path inside one .blend and save it in place."""
    blend = Path(blend_file).expanduser().resolve()
    old = Path(old_path).expanduser().resolve()
    new = Path(new_path).expanduser().resolve()
    with tempfile.TemporaryDirectory(prefix="eli_lab_relocate_") as temp_dir:
        script = Path(temp_dir) / "relocate.py"
        script.write_text(RELOCATE_SCRIPT, encoding="utf-8")
        process = subprocess.run(
            [blender_executable, "--background", str(blend), "--python", str(script), "--", str(old), str(new)],
            capture_output=True,
            text=True,
            check=False,
        )
    if process.returncode != 0:
        raise RuntimeError(f"Blender relocation failed: {process.stderr.strip()[-2000:]}")
    return "ELI_LAB_RELOCATED=1" in process.stdout


def relocate_texture_with_references(root: str | Path, source: str | Path, destination: str | Path, blend_files: list[str | Path], blender_executable: str) -> list[Path]:
    """Move one texture and repair every known Blender reference before finalizing."""
    root_path = Path(root).expanduser().resolve()
    source_path = (root_path / source).resolve() if not Path(source).is_absolute() else Path(source).resolve()
    destination_path = (root_path / destination).resolve() if not Path(destination).is_absolute() else Path(destination).resolve()
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    if destination_path.exists():
        raise FileExistsError(destination_path)

    changed: list[Path] = []
    for blend in blend_files:
        blend_path = (root_path / blend).resolve() if not Path(blend).is_absolute() else Path(blend).resolve()
        if repair_blend_texture_reference(blend_path, source_path, destination_path, blender_executable):
            changed.append(blend_path)

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source_path), str(destination_path))
    return changed
