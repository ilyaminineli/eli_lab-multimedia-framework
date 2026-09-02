"""Project management services for the ELI LAB multimedia framework."""

from .blender import provision_blender_file
from .documentation import build_project_markdown, write_project_markdown
from .metadata import ProjectMetadata, load_metadata, save_metadata
from .templates import ProjectStructure, ProjectTemplate, create_project_structure
from .validation import ValidationIssue, ValidationReport, validate_project

__all__ = [
    "ProjectMetadata",
    "ProjectStructure",
    "ProjectTemplate",
    "ValidationIssue",
    "ValidationReport",
    "build_project_markdown",
    "create_project_structure",
    "load_metadata",
    "provision_blender_file",
    "save_metadata",
    "validate_project",
    "write_project_markdown",
]
