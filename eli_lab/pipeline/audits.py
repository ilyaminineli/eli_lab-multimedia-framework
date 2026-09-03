"""Project-wide audits that turn the eli_lab workflow into actionable findings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eli_lab.production.blender_inspection import find_blender, inspect_project
from eli_lab.production.dependencies import discover_dependencies
from eli_lab.production.intelligence import IMAGE_EXTENSIONS, discover_texture_sets
from eli_lab.production.materials import plan_texture_relocation
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
        findings.append(
            AuditFinding(
                "metadata", "warning", ".", "Project metadata has not been generated."
            )
        )

    for entity in discover_entities(root_path):
        metadata_path = Path(entity.path)
        if metadata_path.is_file():
            metadata_path = metadata_path.with_name(f"{metadata_path.stem}.entity.json")
        else:
            metadata_path = metadata_path / "entity.json"
        if not metadata_path.exists():
            findings.append(
                AuditFinding(
                    "entity_documentation",
                    "warning",
                    entity.relative_path,
                    "Entity has no metadata record.",
                )
            )

    for texture_set in discover_texture_sets(root_path):
        if texture_set.missing_channels:
            findings.append(
                AuditFinding(
                    "texture_sets",
                    "warning",
                    texture_set.name,
                    "Missing channels: " + ", ".join(texture_set.missing_channels),
                )
            )
        resolutions = {
            info.resolution_hint for info in texture_set.files if info.resolution_hint
        }
        if len(resolutions) > 1:
            findings.append(
                AuditFinding(
                    "texture_resolution",
                    "info",
                    texture_set.name,
                    "Mixed resolution hints: " + ", ".join(sorted(resolutions)),
                )
            )

    canonical_texture_dir = (root_path / "Assets" / "Textures").resolve()
    for source, destination in plan_texture_relocation(root_path):
        findings.append(
            AuditFinding(
                "texture_location",
                "warning",
                str(source),
                f"Texture is outside the canonical texture library; candidate relocation: {destination}.",
            )
        )

    dependencies = discover_dependencies(root_path)
    for dependency in dependencies:
        if dependency.confidence < 0.8:
            findings.append(
                AuditFinding(
                    "dependency_review",
                    "info",
                    str(dependency.source),
                    f"Low-confidence relationship to {dependency.target}.",
                )
            )

    blender = find_blender()
    if blender:
        references = inspect_project(root_path, blender_executable=blender)
        for reference in references:
            if reference.status == "missing":
                findings.append(
                    AuditFinding(
                        "blender_reference",
                        "error",
                        str(reference.blend_file),
                        f"Missing {reference.kind} reference: {reference.resource}",
                    )
                )
            elif reference.resource.suffix.casefold() in IMAGE_EXTENSIONS:
                resource = (
                    root_path / reference.resource
                    if not reference.resource.is_absolute()
                    else reference.resource
                )
                try:
                    resource.relative_to(canonical_texture_dir)
                except ValueError:
                    findings.append(
                        AuditFinding(
                            "texture_reference_location",
                            "warning",
                            str(reference.blend_file),
                            f"Blender directly references a texture outside Assets/Textures: {reference.resource}",
                        )
                    )
    else:
        findings.append(
            AuditFinding(
                "blender_inspection",
                "info",
                ".",
                "Blender was not found on PATH; authoritative .blend inspection was skipped.",
            )
        )

    return findings
