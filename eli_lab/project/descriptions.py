"""Description and Markdown generation for project entities."""

from __future__ import annotations

from pathlib import Path

from .entities import ProjectEntity, group_entities
from .workspace import EntityMetadata, load_entity_metadata, save_entity_metadata


def description_seed(entity: ProjectEntity) -> str:
    labels = {
        "character": "Character / character asset used by the production.",
        "location": "Location / environment used by the production.",
        "asset": "Reusable production asset or model.",
        "scene": "Production scene containing the assembled shot or environment.",
        "script": "Pipeline or production script associated with the project.",
        "test_scene": "Experimental or validation scene used during development.",
    }
    return labels.get(entity.kind, "Production entity managed by the ELI LAB pipeline.")


def ensure_entity_metadata(root: str | Path, entity: ProjectEntity) -> EntityMetadata:
    metadata = load_entity_metadata(Path(root) / entity.path)
    if not metadata.description:
        metadata.description = description_seed(entity)
    if not metadata.name:
        metadata.name = entity.name
    if not metadata.kind:
        metadata.kind = entity.kind
    return metadata


def build_entity_markdown(entity: ProjectEntity, metadata: EntityMetadata) -> str:
    file_list = "\n".join(f"- `{path.as_posix()}`" for path in entity.files) or "- No files discovered"
    return f"""# {metadata.name}\n\n**Type:** {metadata.kind.replace('_', ' ').title()}  \n**Status:** {metadata.status}\n\n## Description\n\n{metadata.description.strip() or description_seed(entity)}\n\n## Location\n\n`{entity.path.as_posix()}`\n\n## Files\n\n{file_list}\n\n## Notes\n\n{metadata.notes.strip() or "None"}\n"""


def write_entity_markdown(root: str | Path, entity: ProjectEntity) -> Path:
    root_path = Path(root).expanduser().resolve()
    metadata = ensure_entity_metadata(root_path, entity)
    metadata_path = save_entity_metadata(root_path / entity.path, metadata)
    output = metadata_path.parent / "README.md"
    output.write_text(build_entity_markdown(entity, metadata), encoding="utf-8")
    return output


def build_inventory_markdown(summary) -> str:
    """Build a project README inventory from the live filesystem state."""
    name = summary.metadata.project_name if summary.metadata else summary.root.name
    description = summary.metadata.project_description if summary.metadata else ""
    grouped = group_entities(summary.entities)
    sections: list[str] = []
    order = ("scene", "character", "location", "asset", "script", "test_scene")
    titles = {
        "scene": "Scenes",
        "character": "Characters",
        "location": "Locations",
        "asset": "Assets",
        "script": "Scripts",
        "test_scene": "Test Scenes",
    }
    for kind in order:
        items = grouped.get(kind, [])
        if not items:
            continue
        lines = []
        for entity in sorted(items, key=lambda item: item.name.casefold()):
            metadata = ensure_entity_metadata(summary.root, entity)
            lines.append(f"- **{metadata.name}** — {metadata.description or description_seed(entity)} (`{entity.path.as_posix()}`)")
        sections.append(f"## {titles[kind]}\n\n" + "\n".join(lines))

    pipeline = "\n".join(f"- `{path.as_posix()}`" for path in summary.files[:50]) or "- No files discovered"
    return f"""# {name}\n\n{description.strip() or "Production project managed through the ELI LAB Multimedia Framework."}\n\n## Project Inventory\n\n{chr(10).join(sections) or "No semantic entities discovered yet."}\n\n## Framework Files\n\n{pipeline}\n"""


def write_inventory_markdown(summary, output: str | Path | None = None) -> Path:
    target = Path(output).expanduser().resolve() if output else summary.root / "README.md"
    target.write_text(build_inventory_markdown(summary), encoding="utf-8")
    return target
