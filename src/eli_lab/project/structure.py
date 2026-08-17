"""Project directory structure generation and template expansion."""

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


@dataclass(frozen=True, slots=True)
class ProjectTemplate:
    """Optional named content for a project template.

    Names are kept as relative project entries. The GUI is responsible only for
    collecting these values; filesystem creation stays in this module.
    """

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


def create_project_structure(
    root: str | Path,
    structure: ProjectStructure | None = None,
    template: ProjectTemplate | None = None,
) -> list[Path]:
    """Create a project directory tree and return directories created."""
    root_path = Path(root).expanduser().resolve()
    selected = structure or ProjectStructure()
    created: list[Path] = []

    if template:
        errors = template.validate()
        if errors:
            raise ValueError("Invalid project template: " + "; ".join(errors))
        root_path = root_path / template.project_name
        legacy_folders = (
            f"{template.project_name}_characters",
            f"{template.project_name}_locations",
            f"{template.project_name}_assets",
            f"{template.project_name}_scripts",
            f"{template.project_name}_misc",
        )
        folders = tuple(legacy_folders)
    else:
        folders = selected.folders

    for relative_path in folders:
        directory = root_path / relative_path
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(directory)

    if template:
        characters_root = root_path / f"{template.project_name}_characters"
        locations_root = root_path / f"{template.project_name}_locations"
        assets_root = root_path / f"{template.project_name}_assets"

        for name in template.characters:
            directory = characters_root / f"{template.project_name}_{name}"
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                created.append(directory)

        for name, subfolders in template.locations:
            location_root = locations_root / f"{template.project_name}_{name}"
            if not location_root.exists():
                location_root.mkdir(parents=True, exist_ok=True)
                created.append(location_root)
            for subfolder in subfolders:
                directory = location_root / f"{template.project_name}_{subfolder}"
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                    created.append(directory)

        for name, subfolders in template.assets:
            asset_root = assets_root / f"{template.project_name}_{name}"
            if not asset_root.exists():
                asset_root.mkdir(parents=True, exist_ok=True)
                created.append(asset_root)
            for subfolder in subfolders:
                directory = asset_root / f"{template.project_name}_{subfolder}"
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                    created.append(directory)

    return created
