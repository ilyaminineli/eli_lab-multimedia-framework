"""Registry for the PySide6 desktop tools."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    key: str
    name: str
    category: str
    description: str = ""


TOOLS: tuple[ToolDefinition, ...] = (
    ToolDefinition("workspace", "Project Workspace", "Project", "Open, scan, edit, normalize and document an existing production project."),
    ToolDefinition("template", "Advanced Template System", "Project", "Create standardized project trees and entity folders."),
    ToolDefinition("metadata", "Project Metadata", "Project", "Create and edit canonical project metadata."),
    ToolDefinition("documentation", "Project Documentation", "Project", "Generate project README documentation."),
    ToolDefinition("file_validation", "File Validation", "Validation", "Compare a project against a saved file snapshot."),
    ToolDefinition("project_validation", "Project Validation", "Validation", "Validate required project directories."),
    ToolDefinition("texture_conversion", "Texture Conversion", "Assets", "Convert supported source textures to PNG."),
    ToolDefinition("texture_optimization", "Texture Optimization", "Assets", "Optimize PNG textures with pngquant."),
    ToolDefinition("renaming", "File Renaming", "Automation", "Preview and apply safe batch filename operations."),
    ToolDefinition("tasks", "Task Management", "Analysis", "Create and track production tasks."),
    ToolDefinition("performance", "Performance Analysis", "Analysis", "Analyze historical task performance."),
)
