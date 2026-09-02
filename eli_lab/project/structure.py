"""Backward-compatible imports for the project template service.

New code should import from :mod:`eli_lab.project.templates`.
"""

from .templates import ProjectStructure, ProjectTemplate, create_project_structure

__all__ = ["ProjectStructure", "ProjectTemplate", "create_project_structure"]
