"""Production intelligence services for eli_lab."""

from .blender_inspection import (
    BlenderReference,
    find_blender,
    inspect_blend,
    inspect_project,
)
from .dependencies import Dependency, dependencies_for, discover_dependencies
from .intelligence import (
    TextureInfo,
    TextureSet,
    discover_texture_sets,
    group_texture_set,
    inspect_texture,
)
from .materials import (
    MaterialRecord,
    apply_texture_relocation,
    canonical_texture_directory,
    discover_material_records,
    plan_texture_relocation,
)
from .texture_relocation import (
    TextureRelocationCandidate,
    TextureRelocationResult,
    plan_referenced_texture_relocations,
    relocate_texture_candidate,
)

__all__ = [
    "BlenderReference",
    "Dependency",
    "MaterialRecord",
    "TextureInfo",
    "TextureRelocationCandidate",
    "TextureRelocationResult",
    "TextureSet",
    "apply_texture_relocation",
    "canonical_texture_directory",
    "dependencies_for",
    "discover_dependencies",
    "discover_material_records",
    "discover_texture_sets",
    "find_blender",
    "group_texture_set",
    "inspect_blend",
    "inspect_project",
    "inspect_texture",
    "plan_referenced_texture_relocations",
    "plan_texture_relocation",
    "relocate_texture_candidate",
]
