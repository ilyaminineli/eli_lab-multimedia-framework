"""Central registry for the current desktop tools.

The registry is intentionally data-only so the launcher can later switch from
legacy script processes to native in-process GUI components without changing
its navigation structure.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    category: str
    script: str
    description: str = ""


TOOLS: tuple[ToolDefinition, ...] = (
    ToolDefinition("Advanced Template System", "Project", "advanced_template_system", "Create standardized project trees."),
    ToolDefinition("Project Metadata", "Project", "project_metadata_integration", "Create and edit canonical project metadata."),
    ToolDefinition("Project Documentation", "Project", "project_documentation_generator", "Generate project README documentation."),
    ToolDefinition("File Validation", "Validation", "file_validation", "Compare a project against saved file state."),
    ToolDefinition("Project Validation", "Validation", "project_validation", "Provision missing Blender templates."),
    ToolDefinition("Texture Conversion", "Assets", "texture_batch_converter", "Convert source textures to PNG."),
    ToolDefinition("Texture Optimization", "Assets", "texture_batch_optimising_tool", "Optimize PNG textures with pngquant."),
    ToolDefinition("File Renaming", "Automation", "custom_file_renaming", "Preview and apply batch filename operations."),
    ToolDefinition("Task Management", "Analysis", "task_assigner", "Create and track production tasks."),
    ToolDefinition("Performance Analysis", "Analysis", "historical_performance_analyzer", "Analyze historical task performance."),
)
