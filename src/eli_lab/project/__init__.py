"""Project management services for the ELI LAB multimedia framework."""

from .metadata import ProjectMetadata, load_metadata, save_metadata
from .structure import ProjectStructure, create_project_structure
from .validation import ValidationIssue, ValidationReport, validate_project

__all__ = [
    "ProjectMetadata",
    "ProjectStructure",
    "ValidationIssue",
    "ValidationReport",
    "create_project_structure",
    "load_metadata",
    "save_metadata",
    "validate_project",
]
