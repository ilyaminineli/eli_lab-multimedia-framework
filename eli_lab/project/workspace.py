"""High-level project workspace operations built on the existing services."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .entities import ENTITY_DIRECTORIES, ProjectEntity, discover_entities, discover_project_files, group_entities
from .metadata import METADATA_FILENAME, ProjectMetadata, load_metadata, save_metadata

WORKSPACE_DIRNAME = ".eli_lab"
HISTORY_FILENAME = "history.jsonl"
ENTITY_METADATA_FILENAME = "entity.json"
FILE_ENTITY_METADATA_SUFFIX = ".entity.json"


@dataclass(slots=True)
class EntityMetadata:
    """Human-editable metadata for a production entity."""

    name: str
    kind: str
    description: str = ""
    status: str = "In Development"
    notes: str = ""


@dataclass(slots=True)
class WorkspaceSummary:
    root: Path
    metadata: ProjectMetadata | None
    entities: list[ProjectEntity]
    files: list[Path]

    @property
    def counts(self) -> dict[str, int]:
        return {kind: len(items) for kind, items in group_entities(self.entities).items()}


def workspace_dir(root: str | Path) -> Path:
    return Path(root).expanduser().resolve() / WORKSPACE_DIRNAME


def history_path(root: str | Path) -> Path:
    return workspace_dir(root) / HISTORY_FILENAME


def entity_metadata_path(entity_path: str | Path) -> Path:
    path = Path(entity_path).expanduser().resolve()
    if path.is_file():
        return path.with_name(f"{path.stem}{FILE_ENTITY_METADATA_SUFFIX}")
    if path.suffix and not path.exists():
        return path.with_name(f"{path.name}{FILE_ENTITY_METADATA_SUFFIX}")
    return path / ENTITY_METADATA_FILENAME


def load_entity_metadata(entity_path: str | Path) -> EntityMetadata:
    target = Path(entity_path).expanduser().resolve()
    path = entity_metadata_path(target)
    if not path.exists():
        return EntityMetadata(name=target.stem if target.is_file() else target.name, kind="asset")
    data = json.loads(path.read_text(encoding="utf-8"))
    defaults = asdict(EntityMetadata("", "asset"))
    return EntityMetadata(**{field: data.get(field, default) for field, default in defaults.items()})


def save_entity_metadata(entity_path: str | Path, metadata: EntityMetadata) -> Path:
    path = entity_metadata_path(entity_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(metadata), indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def record_history(root: str | Path, operation: str, target: str = "", details: str = "") -> Path:
    path = history_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operation": operation,
        "target": target,
        "details": details,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path


def load_history(root: str | Path, limit: int = 200) -> list[dict[str, str]]:
    path = history_path(root)
    if not path.exists():
        return []
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    entries = [json.loads(line) for line in lines[-limit:]]
    return list(reversed(entries))


def scan_workspace(root: str | Path) -> WorkspaceSummary:
    """Read an existing project without requiring it to have been created by ELI LAB."""
    root_path = Path(root).expanduser().resolve()
    if not root_path.is_dir():
        raise FileNotFoundError(root_path)
    metadata = None
    metadata_file = root_path / METADATA_FILENAME
    if metadata_file.exists():
        metadata = load_metadata(root_path)
    entities = discover_entities(root_path)
    return WorkspaceSummary(root_path, metadata, entities, discover_project_files(root_path))


def entity_path(root: str | Path, kind: str, name: str) -> Path:
    try:
        parent = ENTITY_DIRECTORIES[kind]
    except KeyError as exc:
        raise ValueError(f"Unsupported entity kind: {kind}") from exc
    return Path(root).expanduser().resolve() / parent / name


def ensure_workspace(root: str | Path, metadata: ProjectMetadata | None = None) -> Path:
    """Create the framework bookkeeping directory without changing project content."""
    path = workspace_dir(root)
    path.mkdir(parents=True, exist_ok=True)
    if metadata:
        save_metadata(metadata, root)
    return path
