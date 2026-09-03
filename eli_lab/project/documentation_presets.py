"""Preset-based, project-aware Markdown documentation generation."""

from __future__ import annotations

from pathlib import Path

from .entities import ProjectEntity, group_entities
from .metadata import ProjectMetadata
from .workspace import WorkspaceSummary

PRESETS = {
    "project": "Project README",
    "catalogue": "Entity Catalogue",
    "pipeline": "Pipeline Report",
    "compact": "Compact Overview",
}


def _entity_lines(entities: list[ProjectEntity]) -> str:
    grouped = group_entities(entities)
    order = ("character", "location", "asset", "scene", "script", "test_scene")
    sections: list[str] = []
    for kind in order:
        items = grouped.get(kind, [])
        if not items:
            continue
        sections.append(
            f"## {kind.replace('_', ' ').title()}s\n\n"
            + "\n".join(
                f"- **{item.name}** — `{item.relative_path}` ({len(item.files)} files)"
                for item in items
            )
        )
    return "\n\n".join(sections) or "No recognized entities yet."


def build_preset_markdown(summary: WorkspaceSummary, preset: str = "project") -> str:
    metadata: ProjectMetadata | None = summary.metadata
    title = metadata.project_name if metadata else summary.root.name
    description = metadata.project_description.strip() if metadata else ""
    counts = summary.counts
    if preset == "compact":
        return f"# {title}\n\n{description}\n\n**Files:** {len(summary.files)}  \n**Entities:** {len(summary.entities)}  \n**Profile:** managed by eli_lab\n"
    if preset == "pipeline":
        rows = (
            "\n".join(
                f"- {kind.title()}: {count}" for kind, count in sorted(counts.items())
            )
            or "- No semantic entities discovered"
        )
        return f"# {title} — Pipeline Report\n\n**Project root:** `{summary.root}`\n\n**Files:** {len(summary.files)}\n\n{rows}\n\n## Structure\n\nGenerated and normalized through eli_lab project services.\n"
    if preset == "catalogue":
        return f"# {title} — Entity Catalogue\n\n{_entity_lines(summary.entities)}\n"
    themes = metadata.key_themes if metadata else ""
    return (
        f"# {title}\n\n"
        f"**Status:** {metadata.project_status if metadata else 'In Development'}  \n"
        f"**Project Code:** {metadata.project_code if metadata else ''}\n\n"
        f"## Synopsis\n\n{description or 'Description not written yet.'}\n\n"
        f"## Key Themes\n\n{themes or 'Not specified.'}\n\n"
        f"## Project Inventory\n\n{_entity_lines(summary.entities)}\n\n"
        f"## Pipeline\n\nThis project is managed with the eli_lab production pipeline.\n"
    )


def write_preset_markdown(
    summary: WorkspaceSummary, output: str | Path, preset: str = "project"
) -> Path:
    path = Path(output).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_preset_markdown(summary, preset), encoding="utf-8")
    return path
