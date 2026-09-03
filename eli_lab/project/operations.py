"""Safe high-level production operations over existing project services."""

from __future__ import annotations

from pathlib import Path

from .descriptions import write_entity_markdown, write_inventory_markdown
from .entities import ProjectEntity, discover_entities
from .templates import create_project_structure
from .workspace import (
    EntityMetadata,
    entity_path,
    record_history,
    save_entity_metadata,
    scan_workspace,
)


def create_entity(
    root: str | Path, kind: str, name: str, *, subfolders: tuple[str, ...] = ()
) -> ProjectEntity:
    """Create a new semantic entity in a standardized project."""
    root_path = Path(root).expanduser().resolve()
    path = entity_path(root_path, kind, name)
    if path.exists():
        raise FileExistsError(f"Entity already exists: {path}")
    path.mkdir(parents=True)
    for subfolder in subfolders:
        (path / subfolder).mkdir(parents=True, exist_ok=True)
    metadata = EntityMetadata(name=name, kind=kind)
    save_entity_metadata(path, metadata)
    entity = next(
        item
        for item in discover_entities(root_path)
        if item.path == path.relative_to(root_path)
    )
    write_entity_markdown(root_path, entity)
    record_history(root_path, "create_entity", entity.relative_path, f"kind={kind}")
    return entity


def add_entity_to_standard_project(
    root: str | Path, kind: str, name: str
) -> ProjectEntity:
    """Create an entity using the Daly-style scene/asset substructure."""
    defaults = {
        "character": ("references", "textures"),
        "location": ("assets", "textures"),
        "asset": (),
        "scene": ("assets", "textures"),
        "test_scene": (),
    }
    return create_entity(root, kind, name, subfolders=defaults.get(kind, ()))


def refresh_project_documentation(root: str | Path) -> Path:
    """Regenerate entity READMEs and the project inventory from live files."""
    summary = scan_workspace(root)
    for entity in summary.entities:
        write_entity_markdown(summary.root, entity)
    output = write_inventory_markdown(summary)
    record_history(
        summary.root,
        "refresh_documentation",
        output.name,
        f"entities={len(summary.entities)}",
    )
    return output


def regenerate_structure(
    root: str | Path, project_name: str, *, structure=None
) -> list[Path]:
    """Generate missing standard directories without deleting existing work."""
    from .templates import ProjectTemplate, ProjectStructure

    blueprint = structure or ProjectStructure.daly()
    template = ProjectTemplate(project_name=project_name)
    paths = create_project_structure(root, blueprint, template)
    record_history(root, "regenerate_structure", project_name, f"created={len(paths)}")
    return paths
