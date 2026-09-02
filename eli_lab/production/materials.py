"""Material-library discovery and canonical texture placement helpers."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from .intelligence import IMAGE_EXTENSIONS, TextureSet, discover_texture_sets


@dataclass(frozen=True, slots=True)
class MaterialRecord:
    name: str
    source_files: tuple[Path, ...]
    texture_sets: tuple[str, ...]
    location: Path | None = None


def material_name_from_path(path: str | Path) -> str:
    stem = Path(path).stem
    stem = re.sub(r"(?:[_ -]?(?:material|mat|basecolor|base_color|diffuse|albedo|normal|roughness|metallic|height|ao|opacity|alpha|mask))(?:[_ -]?\d{1,2}k)?$", "", stem, flags=re.I)
    return stem.strip(" _-") or Path(path).stem


def discover_material_records(root: str | Path) -> list[MaterialRecord]:
    root_path = Path(root).expanduser().resolve()
    records: dict[str, list[Path]] = {}
    for path in root_path.rglob("*.blend"):
        if any(part.casefold() in {"materials", "material library", "material_library"} for part in path.parts):
            records.setdefault(material_name_from_path(path).casefold(), []).append(path)
    texture_sets = discover_texture_sets(root_path)
    by_name = {item.name.casefold(): item.name for item in texture_sets}
    result: list[MaterialRecord] = []
    for key, sources in sorted(records.items()):
        result.append(MaterialRecord(
            name=sources[0].stem,
            source_files=tuple(sorted(p.relative_to(root_path) for p in sources)),
            texture_sets=tuple(value for name, value in by_name.items() if key in name or name in key),
            location=sources[0].relative_to(root_path).parent,
        ))
    return result


def canonical_texture_directory(root: str | Path) -> Path:
    return Path(root).expanduser().resolve() / "Assets" / "Textures"


def plan_texture_relocation(root: str | Path) -> list[tuple[Path, Path]]:
    """Plan moves for textures outside Assets/Textures without overwriting files."""
    root_path = Path(root).expanduser().resolve()
    canonical = canonical_texture_directory(root_path)
    plan: list[tuple[Path, Path]] = []
    for texture in sorted(root_path.rglob("*")):
        if not texture.is_file() or texture.suffix.casefold() not in IMAGE_EXTENSIONS:
            continue
        try:
            texture.relative_to(canonical)
            continue
        except ValueError:
            pass
        destination = canonical / texture.name
        if destination.exists():
            destination = canonical / texture.relative_to(root_path).with_suffix(texture.suffix)
            # Preserve the source-relative context when a canonical filename exists.
            destination = canonical / "_relocated" / texture.relative_to(root_path)
        plan.append((texture.relative_to(root_path), destination.relative_to(root_path)))
    return plan


def apply_texture_relocation(root: str | Path, minimum_confidence: float = 1.0) -> list[tuple[Path, Path]]:
    """Move only files from a relocation plan, never overwrite existing data."""
    root_path = Path(root).expanduser().resolve()
    canonical = canonical_texture_directory(root_path)
    canonical.mkdir(parents=True, exist_ok=True)
    moved: list[tuple[Path, Path]] = []
    for source_rel, destination_rel in plan_texture_relocation(root_path):
        source = root_path / source_rel
        destination = root_path / destination_rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.exists() and not destination.exists():
            shutil.move(str(source), str(destination))
            moved.append((source_rel, destination_rel))
    return moved
