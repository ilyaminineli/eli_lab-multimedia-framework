"""Project templates and directory-tree generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProjectStructure:
    """Canonical directory layout for new ELI LAB projects."""

    folders: tuple[str, ...] = field(
        default=(
            "assets",
            "assets/textures",
            "assets/models",
            "assets/characters",
            "assets/locations",
            "scenes",
            "source",
            "renders",
            "exports",
            "docs",
            "tasks",
        )
    )


@dataclass(frozen=True, slots=True)
class ProjectTemplate:
    """Project-specific content layered onto :class:`ProjectStructure`."""

    project_name: str
    characters: tuple[str, ...] = ()
    locations: tuple[tuple[str, tuple[str, ...]], ...] = ()
    assets: tuple[tuple[str, tuple[str, ...]], ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.project_name.strip():
            errors.append("project_name is required")
        if any(not name.strip() for name in self.characters):
            errors.append("character names cannot be empty")
        if any(not name.strip() for name, _ in self.locations):
            errors.append("location names cannot be empty")
        if any(not name.strip() for name, _ in self.assets):
            errors.append("asset names cannot be empty")
        return errors


def _create_directory(path: Path, created: list[Path]) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        created.append(path)


def create_project_structure(
    root: str | Path,
    structure: ProjectStructure | None = None,
    template: ProjectTemplate | None = None,
) -> list[Path]:
    """Create a canonical project tree and return directories created.

    The named entities are stored inside their semantic asset categories rather
    than producing project-name-prefixed folders at the project root.
    """
    root_path = Path(root).expanduser().resolve()
    selected = structure or ProjectStructure()
    created: list[Path] = []

    if template:
        errors = template.validate()
        if errors:
            raise ValueError("Invalid project template: " + "; ".join(errors))
        root_path /= template.project_name

    for relative_path in selected.folders:
        _create_directory(root_path / relative_path, created)

    if not template:
        return created

    for name in template.characters:
        _create_directory(root_path / "assets" / "characters" / name, created)

    for name, subfolders in template.locations:
        location_root = root_path / "assets" / "locations" / name
        _create_directory(location_root, created)
        for subfolder in subfolders:
            _create_directory(location_root / subfolder, created)

    for name, subfolders in template.assets:
        asset_root = root_path / "assets" / "models" / name
        _create_directory(asset_root, created)
        for subfolder in subfolders:
            _create_directory(asset_root / subfolder, created)

    return created
