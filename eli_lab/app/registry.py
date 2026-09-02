"""Registry of temporary and future ELI LAB desktop tools."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    category: str
    script: str
    description: str = ""


TOOLS: tuple[ToolDefinition, ...] = (
    ToolDefinition("Advanced Template System", "Project", "in_progress/advanced_template_system.py", "Create standardized project trees."),
    ToolDefinition("Project Metadata", "Project", "in_progress/project_metadata_integration.py", "Create and edit canonical project metadata."),
    ToolDefinition("Project Documentation", "Project", "in_progress/project_documentation_generator.py", "Generate project README documentation."),
    ToolDefinition("File Validation", "Validation", "in_progress/file_validation.py", "Compare a project against saved file state."),
    ToolDefinition("Project Validation", "Validation", "in_progress/project_validation.py", "Provision missing Blender templates."),
    ToolDefinition("Texture Conversion", "Assets", "in_progress/texture_batch_converter.py", "Convert source textures to PNG."),
    ToolDefinition("Texture Optimization", "Assets", "in_progress/texture_batch_optimising_tool.py", "Optimize PNG textures with pngquant."),
    ToolDefinition("File Renaming", "Automation", "in_progress/custom_file_renaming.py", "Preview and apply batch filename operations."),
    ToolDefinition("Task Management", "Analysis", "in_progress/task_assigner.py", "Create and track production tasks."),
    ToolDefinition("Performance Analysis", "Analysis", "in_progress/historical_performance_analyzer.py", "Analyze historical task performance."),
)
