"""Project templates and standardized production-tree generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProjectStructure:
    """Directory blueprint used when generating a production repository.

    The legacy lowercase layout remains the default for compatibility. The
    ``daly`` blueprint mirrors the production hierarchy used by the
    Daly-Syndrome project: semantic top-level collections, Main Scenes, and
    scene-local working data.
    """

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

    @classmethod
    def daly(cls) -> "ProjectStructure":
        return cls(
            folders=(
                "Assets",
                "Assets/Textures",
                "Characters",
                "Locations",
                "Scripts",
                "Test Scenes",
                "Scenes",
                "Scenes/Main Scenes",
                "Docs",
                "Renders",
                "Exports",
            )
        )


@dataclass(frozen=True, slots=True)
class ProjectTemplate:
    """Project-specific content layered onto a :class:`ProjectStructure`."""

    project_name: str
    characters: tuple[str, ...] = ()
    locations: tuple[tuple[str, tuple[str, ...]], ...] = ()
    assets: tuple[tuple[str, tuple[str, ...]], ...] = ()
    scenes: tuple[tuple[str, tuple[str, ...]], ...] = ()
    test_scenes: tuple[str, ...] = ()

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
        if any(not name.strip() for name, _ in self.scenes):
            errors.append("scene names cannot be empty")
        if any(not name.strip() for name in self.test_scenes):
            errors.append("test scene names cannot be empty")
        return errors


def _create_directory(path: Path, created: list[Path]) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        created.append(path)


def _create_entity(
    root: Path,
    relative_root: str,
    name: str,
    subfolders: tuple[str, ...],
    created: list[Path],
) -> None:
    entity_root = root / relative_root / name
    _create_directory(entity_root, created)
    for subfolder in subfolders:
        _create_directory(entity_root / subfolder, created)


def create_project_structure(
    root: str | Path,
    structure: ProjectStructure | None = None,
    template: ProjectTemplate | None = None,
) -> list[Path]:
    """Create a canonical project tree and return directories created."""
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

    is_daly = any(folder == "Scenes/Main Scenes" for folder in selected.folders)
    if is_daly:
        for name in template.characters:
            _create_entity(
                root_path, "Characters", name, ("references", "textures"), created
            )
        for name, subfolders in template.locations:
            _create_entity(
                root_path,
                "Locations",
                name,
                subfolders or ("assets", "textures"),
                created,
            )
        for name, subfolders in template.assets:
            _create_entity(root_path, "Assets", name, subfolders or (), created)
        for name, subfolders in template.scenes:
            _create_entity(
                root_path,
                "Scenes/Main Scenes",
                name,
                subfolders or ("assets", "textures"),
                created,
            )
        for name in template.test_scenes:
            _create_entity(root_path, "Test Scenes", name, (), created)
    else:
        for name in template.characters:
            _create_directory(root_path / "assets" / "characters" / name, created)
        for name, subfolders in template.locations:
            _create_entity(root_path, "assets/locations", name, subfolders, created)
        for name, subfolders in template.assets:
            _create_entity(root_path, "assets/models", name, subfolders, created)
        for name, subfolders in template.scenes:
            _create_entity(root_path, "scenes", name, subfolders, created)

    return created
