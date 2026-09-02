"""Project-wide audits that turn the eli_lab workflow into actionable findings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eli_lab.production.dependencies import discover_dependencies
from eli_lab.production.intelligence import discover_texture_sets
from eli_lab.project.entities import discover_entities


@dataclass(frozen=True, slots=True)
class AuditFinding:
    rule: str
    severity: str
    target: str
    message: str


def audit_project(root: str | Path) -> list[AuditFinding]:
    root_path = Path(root).expanduser().resolve()
    findings: list[AuditFinding] = []

    if not (root_path / "project_metadata.json").exists():
        findings.append(AuditFinding("metadata", "warning", ".", "Project metadata has not been generated."))

    for entity in discover_entities(root_path):
        metadata_path = root_path / entity.path / "entity.json"
        if not metadata_path.exists():
            findings.append(AuditFinding("entity_documentation", "warning", entity.relative_path, "Entity has no metadata record."))

    for texture_set in discover_texture_sets(root_path):
        if texture_set.missing_channels:
            findings.append(AuditFinding("texture_sets", "warning", texture_set.name, "Missing channels: " + ", ".join(texture_set.missing_channels)))
        resolutions = {info.resolution_hint for info in texture_set.files if info.resolution_hint}
        if len(resolutions) > 1:
            findings.append(AuditFinding("texture_resolution", "info", texture_set.name, "Mixed resolution hints: " + ", ".join(sorted(resolutions))))

    dependencies = discover_dependencies(root_path)
    for dependency in dependencies:
        if dependency.confidence < 0.8:
            findings.append(AuditFinding("dependency_review", "info", str(dependency.source), f"Low-confidence relationship to {dependency.target}."))
    return findings
