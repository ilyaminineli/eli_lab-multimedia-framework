"""Project directory structure generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProjectStructure:
    """Directories created for a new multimedia project."""

    folders: tuple[str, ...] = field(
        default=(
            "assets",
            "assets/textures",
            "assets/models",
            "assets/characters",
            "assets/locations",
            "scenes",
            "renders",
            "source",
            "docs",
            "exports",
        )
    )


def create_project_structure(root: str | Path, structure: ProjectStructure | None = None) -> list[Path]:
    """Create a project directory tree and return directories created."""
    root_path = Path(root).expanduser().resolve()
    selected = structure or ProjectStructure()
    created: list[Path] = []
    for relative_path in selected.folders:
        directory = root_path / relative_path
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(directory)
    return created
