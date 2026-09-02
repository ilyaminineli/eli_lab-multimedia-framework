"""Project management services for the eli_lab multimedia framework."""

from .blender import provision_blender_file
from .descriptions import build_entity_markdown, write_entity_markdown
from .documentation import build_project_markdown, write_project_markdown
from .documentation_presets import PRESETS, build_preset_markdown, write_preset_markdown
from .entities import ProjectEntity, discover_entities, discover_project_files
from .metadata import ProjectMetadata, load_metadata, save_metadata
from .migration import MigrationOperation, MigrationPlan, ProjectScan, apply_migration, build_migration_plan, generate_entity_metadata, generate_metadata, scan_project
from .operations import add_entity_to_standard_project, create_entity, refresh_project_documentation, regenerate_structure
from .templates import ProjectStructure, ProjectTemplate, create_project_structure
from .validation import ValidationIssue, ValidationReport, validate_project
from .workspace import EntityMetadata, WorkspaceSummary, load_entity_metadata, load_history, save_entity_metadata, scan_workspace

__all__ = [
    "EntityMetadata", "MigrationOperation", "MigrationPlan", "PRESETS", "ProjectEntity", "ProjectMetadata", "ProjectScan", "ProjectStructure", "ProjectTemplate", "ValidationIssue", "ValidationReport", "WorkspaceSummary",
    "add_entity_to_standard_project", "apply_migration", "build_entity_markdown", "build_migration_plan", "build_preset_markdown", "build_project_markdown", "create_entity", "create_project_structure", "discover_entities", "discover_project_files", "generate_entity_metadata", "generate_metadata", "load_entity_metadata", "load_history", "load_metadata", "provision_blender_file", "refresh_project_documentation", "regenerate_structure", "save_entity_metadata", "save_metadata", "scan_project", "scan_workspace", "validate_project", "write_entity_markdown", "write_preset_markdown", "write_project_markdown",
]
