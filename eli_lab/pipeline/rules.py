"""Explicit production-pipeline policies derived from the eli_lab workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eli_lab.production.intelligence import discover_texture_sets


@dataclass(frozen=True, slots=True)
class PipelineRule:
    key: str
    name: str
    category: str
    severity: str = "warning"
    description: str = ""


RULES = (
    PipelineRule(
        "canonical_structure",
        "Canonical project structure",
        "Organization",
        "error",
        "Project uses the configured standard hierarchy.",
    ),
    PipelineRule(
        "entity_documentation",
        "Entity documentation",
        "Documentation",
        "warning",
        "Production entities have editable metadata and generated documentation.",
    ),
    PipelineRule(
        "texture_sets",
        "Texture set completeness",
        "Textures",
        "warning",
        "Recognized texture sets should contain core PBR channels when appropriate.",
    ),
    PipelineRule(
        "relative_paths",
        "Relative project paths",
        "Dependencies",
        "warning",
        "Project relationships should remain portable after the project is moved.",
    ),
)


def audit_texture_sets(root: str | Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for texture_set in discover_texture_sets(root):
        if texture_set.missing_channels:
            findings.append(
                {
                    "rule": "texture_sets",
                    "severity": "warning",
                    "target": texture_set.name,
                    "message": "Missing channels: "
                    + ", ".join(texture_set.missing_channels),
                }
            )
    return findings
