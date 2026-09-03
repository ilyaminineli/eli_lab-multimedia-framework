"""Interactive, reference-aware texture relocation for eli_lab projects."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from eli_lab.project.workspace import record_history

from .blender_inspection import BlenderReference, find_blender, inspect_project
from .intelligence import IMAGE_EXTENSIONS


@dataclass(frozen=True, slots=True)
class TextureRelocationCandidate:
    source: Path
    destination: Path
    blend_files: tuple[Path, ...]
    references: tuple[BlenderReference, ...]
    reason: str
    safe: bool = True


@dataclass(frozen=True, slots=True)
class TextureRelocationResult:
    source: Path
    destination: Path
    repaired_blends: tuple[Path, ...]
    backup_directory: Path


def canonical_texture_directory(root: str | Path) -> Path:
    return Path(root).expanduser().resolve() / "Assets" / "Textures"


def _relative(root: Path, path: Path) -> Path:
    return path.relative_to(root) if path.is_relative_to(root) else path


def _unique_destination(root: Path, source: Path) -> Path:
    canonical = canonical_texture_directory(root)
    destination = canonical / source.name
    if not destination.exists():
        return destination
    destination = canonical / "_relocated" / source.relative_to(root)
    if not destination.exists():
        return destination
    stem, suffix = source.stem, source.suffix
    for index in range(2, 10000):
        candidate = destination.parent / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find a free relocation destination for {source}")


def plan_referenced_texture_relocations(
    root: str | Path, blender_executable: str | None = None
) -> list[TextureRelocationCandidate]:
    """Find textures that Blender actually references outside Assets/Textures."""
    root_path = Path(root).expanduser().resolve()
    canonical = canonical_texture_directory(root_path)
    references = inspect_project(root_path, blender_executable=blender_executable)
    by_resource: dict[Path, list[BlenderReference]] = {}
    for reference in references:
        if reference.kind != "image" or reference.status != "resolved":
            continue
        resource = (
            reference.resource
            if reference.resource.is_absolute()
            else root_path / reference.resource
        )
        resource = resource.resolve()
        if resource.suffix.casefold() not in IMAGE_EXTENSIONS:
            continue
        try:
            resource.relative_to(canonical)
        except ValueError:
            by_resource.setdefault(resource, []).append(reference)

    candidates: list[TextureRelocationCandidate] = []
    for source, refs in sorted(
        by_resource.items(), key=lambda item: str(item[0]).casefold()
    ):
        if not source.exists():
            continue
        destination = _unique_destination(root_path, source)
        blend_files = tuple(
            sorted(
                {reference.blend_file for reference in refs},
                key=lambda item: str(item).casefold(),
            )
        )
        candidates.append(
            TextureRelocationCandidate(
                source=_relative(root_path, source),
                destination=_relative(root_path, destination),
                blend_files=blend_files,
                references=tuple(refs),
                reason=f"Referenced by {len(blend_files)} Blender file(s) but stored outside Assets/Textures.",
                safe=not destination.exists() and bool(blend_files),
            )
        )
    return candidates


REPAIR_SCRIPT = r"""
import bpy
import os
import sys

old_path = os.path.normcase(os.path.abspath(sys.argv[-2]))
new_path = os.path.abspath(sys.argv[-1])
changed = False
for image in bpy.data.images:
    if image.source != 'FILE' or not image.filepath:
        continue
    absolute = os.path.normcase(os.path.abspath(bpy.path.abspath(image.filepath)))
    if absolute == old_path:
        image.filepath = bpy.path.relpath(new_path)
        image.filepath_raw = bpy.path.relpath(new_path)
        changed = True
if changed:
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('ELI_LAB_REPAIRED=' + ('1' if changed else '0'))
"""


def _repair_blend(
    blend_file: Path, old_path: Path, new_path: Path, blender_executable: str
) -> bool:
    with tempfile.TemporaryDirectory(prefix="eli_lab_texture_repair_") as temp_dir:
        script = Path(temp_dir) / "repair.py"
        script.write_text(REPAIR_SCRIPT, encoding="utf-8")
        process = subprocess.run(
            [
                blender_executable,
                "--background",
                str(blend_file),
                "--python",
                str(script),
                "--",
                str(old_path),
                str(new_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    if process.returncode != 0:
        raise RuntimeError(
            f"Blender repair failed for {blend_file}: {process.stderr.strip()[-2000:]}"
        )
    return "ELI_LAB_REPAIRED=1" in process.stdout


def _backup_path(root: Path, blend: Path, stamp: str) -> Path:
    relative = blend.relative_to(root)
    return root / ".eli_lab" / "backups" / stamp / relative


def relocate_texture_candidate(
    root: str | Path,
    candidate: TextureRelocationCandidate,
    blender_executable: str | None = None,
) -> TextureRelocationResult:
    """Apply one candidate transactionally, backing up affected .blend files first."""
    root_path = Path(root).expanduser().resolve()
    blender = blender_executable or find_blender()
    if not blender:
        raise FileNotFoundError("Blender executable was not found on PATH.")
    source = root_path / candidate.source
    destination = root_path / candidate.destination
    if not candidate.safe:
        raise ValueError("This relocation candidate is not marked safe.")
    if not source.exists():
        raise FileNotFoundError(source)
    if destination.exists():
        raise FileExistsError(destination)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = root_path / ".eli_lab" / "backups" / stamp
    backups: list[tuple[Path, Path]] = []
    repaired: list[Path] = []
    moved = False
    try:
        for blend_rel in candidate.blend_files:
            blend = root_path / blend_rel
            backup = _backup_path(root_path, blend, stamp)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(blend, backup)
            backups.append((blend, backup))
        for blend_rel in candidate.blend_files:
            blend = root_path / blend_rel
            if _repair_blend(blend, source, destination, blender):
                repaired.append(blend_rel)
        if set(repaired) != set(candidate.blend_files):
            raise RuntimeError(
                "Not every referencing Blender file confirmed the texture reference; the operation was rolled back."
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        moved = True
        manifest = backup_root / "relocation.json"
        manifest.write_text(
            json.dumps(
                {
                    "operation": "texture_relocation",
                    "source": str(candidate.source),
                    "destination": str(candidate.destination),
                    "blend_files": [str(path) for path in candidate.blend_files],
                    "timestamp": stamp,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        record_history(
            root_path,
            "texture_relocation",
            str(candidate.source),
            f"Moved to {candidate.destination}; repaired {len(repaired)} Blender file(s); backup={backup_root}",
        )
        return TextureRelocationResult(
            candidate.source, candidate.destination, tuple(repaired), backup_root
        )
    except Exception:
        for blend, backup in reversed(backups):
            if backup.exists():
                shutil.copy2(backup, blend)
        if moved and destination.exists() and not source.exists():
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(destination), str(source))
        raise
