"""Markdown documentation generation from project metadata."""

from __future__ import annotations

from pathlib import Path

from .metadata import ProjectMetadata


def build_project_markdown(metadata: ProjectMetadata) -> str:
    """Render canonical project metadata as a human-readable README."""
    themes = [item.strip() for item in metadata.key_themes.split(",") if item.strip()]
    crew = [item.strip() for item in metadata.crew.splitlines() if item.strip()]

    theme_section = "\n".join(f"- {item}" for item in themes) or "- None specified"
    crew_section = "\n".join(f"- **{item}**" for item in crew) or "- None specified"

    return f"""# {metadata.project_name}

**Status:** {metadata.project_status}  
**License:** {metadata.license}  
**Project Code:** {metadata.project_code}

## Synopsis

{metadata.project_description.strip()}

## Client

{metadata.client.strip() or "Not specified"}

## Pipeline

{metadata.pipeline_version.strip() or "Not specified"}

## Lead Artist

{metadata.lead_artist.strip() or "Not specified"}

## Key Themes

{theme_section}

## Crew

{crew_section}

## Contact

{metadata.contact.strip() or "Not specified"}

## Acknowledgements

{metadata.acknowledgements.strip() or "None"}
"""


def write_project_markdown(metadata: ProjectMetadata, output: str | Path) -> Path:
    path = Path(output).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_project_markdown(metadata), encoding="utf-8")
    return path
