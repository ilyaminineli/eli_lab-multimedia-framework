"""Dependency discovery and relationship indexing for production projects."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr", ".webp", ".bmp"}


@dataclass(frozen=True, slots=True)
class Dependency:
    source: Path
    target: Path
    kind: str
    confidence: float = 1.0


def _normal_key(path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "_", path.stem.casefold()).strip("_")


def discover_dependencies(root: str | Path) -> list[Dependency]:
    """Infer safe, explainable file relationships from project conventions."""
    root_path = Path(root).expanduser().resolve()
    files = [p for p in root_path.rglob("*") if p.is_file()]
    dependencies: list[Dependency] = []
    texture_index: dict[str, list[Path]] = {}
    for path in files:
        if path.suffix.casefold() in IMAGE_EXTENSIONS:
            texture_index.setdefault(_normal_key(path), []).append(path)

    for blend in (p for p in files if p.suffix.casefold() == ".blend"):
        stem_key = _normal_key(blend)
        for texture_path in files:
            if texture_path.suffix.casefold() not in IMAGE_EXTENSIONS:
                continue
            if texture_path.parent == blend.parent:
                dependencies.append(
                    Dependency(
                        blend.relative_to(root_path),
                        texture_path.relative_to(root_path),
                        "nearby-resource",
                        0.9,
                    )
                )
            elif stem_key and stem_key in _normal_key(texture_path):
                dependencies.append(
                    Dependency(
                        blend.relative_to(root_path),
                        texture_path.relative_to(root_path),
                        "name-match",
                        0.6,
                    )
                )
    return dependencies


def dependencies_for(root: str | Path, target: str | Path) -> list[Dependency]:
    target_path = Path(target)
    return [
        item
        for item in discover_dependencies(root)
        if item.source == target_path or item.target == target_path
    ]
