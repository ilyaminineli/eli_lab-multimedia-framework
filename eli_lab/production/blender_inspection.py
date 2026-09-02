"""Optional Blender-aware inspection for authoritative asset dependencies."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class BlenderReference:
    blend_file: Path
    resource: Path
    kind: str
    status: str


BLENDER_EXPORT_SCRIPT = r'''
import bpy
import json
import os
import sys

blend_path = bpy.data.filepath
project_root = os.path.abspath(sys.argv[-1])
result = []

def add(path, kind):
    if not path:
        return
    absolute = os.path.abspath(os.path.join(os.path.dirname(blend_path), path)) if not os.path.isabs(path) else os.path.abspath(path)
    result.append({
        "resource": absolute,
        "kind": kind,
        "exists": os.path.exists(absolute),
    })

for image in bpy.data.images:
    if image.source == 'FILE' and image.filepath:
        add(bpy.path.abspath(image.filepath), 'image')

for cache_file in bpy.data.cache_files:
    if cache_file.filepath:
        add(bpy.path.abspath(cache_file.filepath), 'cache')

for library in bpy.data.libraries:
    if library.filepath:
        add(bpy.path.abspath(library.filepath), 'library')

for movie in getattr(bpy.data, 'movieclips', []):
    if movie.filepath:
        add(bpy.path.abspath(movie.filepath), 'movie')

print(json.dumps({"blend_file": blend_path, "references": result}, ensure_ascii=False))
'''


def find_blender() -> str | None:
    """Return a Blender executable found on PATH, if available."""
    return shutil.which("blender") or shutil.which("blender.exe")


def inspect_blend(blend_file: str | Path, project_root: str | Path, blender_executable: str | None = None) -> list[BlenderReference]:
    """Inspect one .blend using Blender's own bpy data model.

    This is authoritative for paths stored in the .blend. It intentionally does
    not guess from folder proximity or filenames.
    """
    blend = Path(blend_file).expanduser().resolve()
    root = Path(project_root).expanduser().resolve()
    executable = blender_executable or find_blender()
    if not executable:
        raise FileNotFoundError("Blender executable was not found on PATH.")
    with tempfile.TemporaryDirectory(prefix="eli_lab_blender_inspect_") as temp_dir:
        script_path = Path(temp_dir) / "inspect.py"
        script_path.write_text(BLENDER_EXPORT_SCRIPT, encoding="utf-8")
        process = subprocess.run(
            [executable, "--background", str(blend), "--python", str(script_path), "--", str(root)],
            capture_output=True,
            text=True,
            check=False,
        )
    if process.returncode != 0:
        raise RuntimeError(f"Blender inspection failed for {blend}: {process.stderr.strip()[-2000:]}")
    payload = None
    for line in reversed(process.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and "references" in line:
            payload = json.loads(line)
            break
    if payload is None:
        raise RuntimeError(f"No inspection payload returned for {blend}.")

    references: list[BlenderReference] = []
    for item in payload.get("references", []):
        resource = Path(item["resource"]).resolve()
        try:
            relative = resource.relative_to(root)
            resource = relative
        except ValueError:
            pass
        references.append(
            BlenderReference(
                blend_file=blend.relative_to(root) if blend.is_relative_to(root) else blend,
                resource=resource,
                kind=str(item.get("kind", "unknown")),
                status="resolved" if item.get("exists") else "missing",
            )
        )
    return references


def inspect_project(project_root: str | Path, blender_executable: str | None = None) -> list[BlenderReference]:
    """Inspect every .blend in a project and return authoritative references."""
    root = Path(project_root).expanduser().resolve()
    result: list[BlenderReference] = []
    for blend in sorted(root.rglob("*.blend")):
        try:
            result.extend(inspect_blend(blend, root, blender_executable=blender_executable))
        except Exception:
            # Keep project-wide audit resilient: one corrupt/unreadable file
            # should not prevent inspection of every other scene.
            continue
    return result
