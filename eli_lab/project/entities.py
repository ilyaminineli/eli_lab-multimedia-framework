"""Semantic entities discovered inside an ELI LAB production project."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


ENTITY_DIRECTORIES = {
    "character": "Characters",
    "location": "Locations",
    "asset": "Assets",
    "scene": "Scenes",
    "script": "Scripts",
    "test_scene": "Test Scenes",
}


@dataclass(slots=True)
class ProjectEntity:
    """A production entity mapped to a directory and its files."""

    name: str
    kind: str
    path: Path
    files: list[Path] = field(default_factory=list)
    description: str = ""

    @property
    def relative_path(self) -> str:
        return self.path.as_posix()

    @property
    def primary_file(self) -> Path | None:
        if not self.files:
            return None
        preferred = [f for f in self.files if f.suffix.lower() in {".blend", ".md", ".py"}]
        return preferred[0] if preferred else self.files[0]

    @property
    def label(self) -> str:
        return self.name


def entity_kind_for_directory(directory: str) -> str | None:
    for kind, name in ENTITY_DIRECTORIES.items():
        if directory.casefold() == name.casefold():
            return kind
    return None


def _files_under(path: Path) -> list[Path]:
    return sorted((p for p in path.rglob("*") if p.is_file()), key=lambda p: p.as_posix().casefold())


def discover_entities(root: str | Path) -> list[ProjectEntity]:
    """Discover semantic production entities using the standard project hierarchy."""
    root_path = Path(root).expanduser().resolve()
    if not root_path.exists():
        raise FileNotFoundError(root_path)

    entities: list[ProjectEntity] = []
    for directory_name in ENTITY_DIRECTORIES.values():
        parent = root_path / directory_name
        if not parent.is_dir():
            continue
        kind = entity_kind_for_directory(directory_name)
        assert kind is not None
        for child in sorted(parent.iterdir(), key=lambda p: p.name.casefold()):
            if child.name.startswith("."):
                continue
            if child.is_dir():
                entities.append(ProjectEntity(child.name, kind, child.relative_to(root_path), _files_under(child)))
            elif kind == "script":
                entities.append(ProjectEntity(child.stem, kind, child.relative_to(root_path), [child.relative_to(root_path)]))

    return entities


def discover_project_files(root: str | Path) -> list[Path]:
    """Return project files while ignoring Git and common cache directories."""
    root_path = Path(root).expanduser().resolve()
    ignored = {".git", ".venv", "__pycache__", ".pytest_cache"}
    return sorted(
        (p.relative_to(root_path) for p in root_path.rglob("*") if p.is_file() and not any(part in ignored for part in p.parts)),
        key=lambda p: p.as_posix().casefold(),
    )


def group_entities(entities: Iterable[ProjectEntity]) -> dict[str, list[ProjectEntity]]:
    grouped: dict[str, list[ProjectEntity]] = {}
    for entity in entities:
        grouped.setdefault(entity.kind, []).append(entity)
    return grouped
