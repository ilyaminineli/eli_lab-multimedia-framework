"""Recognize and safely normalize legacy or mixed project hierarchies."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from .metadata import ProjectMetadata
from .workspace import EntityMetadata, record_history, save_entity_metadata
from .entities import discover_project_files

TOP_LEVEL = ("Assets", "Characters", "Locations", "Scripts", "Test Scenes", "Scenes", "Docs", "Renders", "Exports")
TEXTURES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr", ".webp", ".bmp"}
IGNORED = {".git", ".eli_lab", "__pycache__", ".venv", ".pytest_cache"}

@dataclass(frozen=True, slots=True)
class MigrationOperation:
    source: Path
    destination: Path
    reason: str
    confidence: float = 1.0

@dataclass(slots=True)
class ProjectScan:
    root: Path
    profile: str
    compliance: int
    entities: int
    files: int
    loose_blends: list[Path]
    loose_textures: list[Path]
    uuid_asset_dirs: list[Path]
    scene_asset_dirs: list[Path]
    missing_top_level: list[str]

@dataclass(slots=True)
class MigrationPlan:
    scan: ProjectScan
    operations: list[MigrationOperation]
    create_directories: list[Path]


def _uuidish(name: str) -> bool:
    return bool(re.search(r"_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", name, re.I))


def scan_project(root: str | Path) -> ProjectScan:
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    top = {p.name.casefold() for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")}
    canonical = {name.casefold() for name in TOP_LEVEL}
    has_main = (root / "Scenes" / "Main Scenes").is_dir()
    has_legacy = "characters" in top or "scenes" in top
    if has_main and canonical.issubset(top):
        profile = "canonical-daly"
    elif has_legacy and "scenes" in top:
        profile = "legacy-daly" if "characters" in top else "legacy-generic"
    else:
        profile = "mixed" if top else "unknown"
    compliance = round(len(canonical & top) / len(canonical) * 100)
    files = discover_project_files(root)
    loose_blends = [p for p in files if p.suffix.casefold() == ".blend" and len(p.parts) == 1]
    loose_textures = [p for p in files if p.suffix.casefold() in TEXTURES and len(p.parts) == 1]
    uuid_dirs: list[Path] = []
    scene_asset_dirs: list[Path] = []
    for p in root.rglob("*"):
        if any(part in IGNORED for part in p.parts):
            continue
        if p.is_dir() and _uuidish(p.name) and p.parent.name.casefold() in {"models", "materials", "textures", "hdrs", "scenes"}:
            uuid_dirs.append(p.relative_to(root))
        if p.is_dir() and p.name.casefold() in {"assets", "textures"} and "scenes" in {part.casefold() for part in p.parts[:-1]}:
            scene_asset_dirs.append(p.relative_to(root))
    missing = [name for name in TOP_LEVEL if not (root / name).is_dir()]
    entities = 0
    try:
        from .entities import discover_entities
        entities = len(discover_entities(root))
    except Exception:
        pass
    return ProjectScan(root, profile, compliance, entities, len(files), loose_blends, loose_textures, uuid_dirs, scene_asset_dirs, missing)


def build_migration_plan(scan: ProjectScan) -> MigrationPlan:
    root = scan.root
    ops: list[MigrationOperation] = []
    dirs: set[Path] = set()
    scenes = root / "Scenes" / "Main Scenes"
    assets = root / "Assets"
    chars = root / "Characters"
    for rel in scan.loose_blends:
        source = root / rel
        if (root / "Scenes").is_dir():
            target = scenes / source.stem / source.name
            ops.append(MigrationOperation(source, target, "Loose .blend at project root / legacy Scenes", .98))
            dirs.add(target.parent)
        elif scan.profile in {"mixed", "legacy-generic"}:
            target = root / "Scenes" / source.stem / source.name
            ops.append(MigrationOperation(source, target, "Loose Blender project file", .9))
            dirs.add(target.parent)
    for rel in scan.loose_textures:
        source = root / rel
        target = assets / "Textures" / source.name
        ops.append(MigrationOperation(source, target, "Loose texture -> shared texture library", .98))
        dirs.add(target.parent)
    if chars.is_dir():
        for source in chars.glob("*.blend"):
            target = chars / source.stem / source.name
            ops.append(MigrationOperation(source, target, "Loose character file -> character entity", .98))
            dirs.add(target.parent)
    for rel in scan.uuid_asset_dirs:
        source = root / rel
        bucket = source.parent.name
        target = assets / bucket / source.name
        ops.append(MigrationOperation(source, target, f"UUID asset folder -> shared {bucket}", .92))
        dirs.add(target.parent)
    return MigrationPlan(scan, ops, sorted(dirs, key=lambda p: p.as_posix().casefold()))


def apply_migration(plan: MigrationPlan, minimum_confidence: float = .95) -> list[MigrationOperation]:
    applied: list[MigrationOperation] = []
    for op in plan.operations:
        if op.confidence < minimum_confidence or not op.source.exists() or op.destination.exists():
            continue
        op.destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(op.source), str(op.destination))
        applied.append(op)
    record_history(plan.scan.root, "normalize", plan.scan.profile, f"applied={len(applied)}")
    return applied


def generate_metadata(scan: ProjectScan) -> ProjectMetadata:
    code = re.sub(r"[^A-Za-z0-9]+", "_", scan.root.name).strip("_").upper()[:20] or "PROJECT"
    return ProjectMetadata(
        project_name=scan.root.name,
        project_code=code,
        pipeline_version="ELI LAB",
        project_description=(f"Production project discovered by ELI LAB. Detected profile: {scan.profile}. "
                             f"Contains {scan.entities} recognized entities and {scan.files} files."),
        project_status="In Development",
        key_themes=f"{scan.profile}, multimedia production, Blender",
    )


def generate_entity_metadata(root: str | Path) -> int:
    from .entities import discover_entities
    root = Path(root).expanduser().resolve()
    count = 0
    for entity in discover_entities(root):
        path = root / entity.path
        metadata = path / "entity.json"
        if metadata.exists():
            continue
        save_entity_metadata(path, EntityMetadata(entity.name, entity.kind))
        count += 1
    record_history(root, "generate_entity_metadata", "", f"created={count}")
    return count
