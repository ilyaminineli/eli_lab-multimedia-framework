# Architecture

The framework is moving from standalone Tkinter scripts to a layered Python package.

## Target layers

```text
Application layer
    GUI / CLI / Blender integration
            |
Service layer
    project / assets / automation / analysis
            |
Core layer
    paths / config / filesystem / logging / errors / models
```

## Module mapping

| Legacy tool | Target module |
|---|---|
| `advanced_template_system.py` | `eli_lab.project.templates` |
| `project_metadata_integration.py` | `eli_lab.project.metadata` |
| `project_documentation_generator.py` | `eli_lab.project.documentation` |
| `project_validation.py` | `eli_lab.project.validation` |
| `file_validation.py` | `eli_lab.project.validation` / `eli_lab.core.filesystem` |
| `custom_file_renaming.py` | `eli_lab.automation.renamer` |
| `texture_batch_converter.py` | `eli_lab.assets.textures` |
| `texture_batch_optimising_tool.py` | `eli_lab.assets.optimization` |
| `task_assigner.py` | `eli_lab.analysis.tasks` |
| `historical_performance_analyzer.py` | `eli_lab.analysis.performance` |
| `init.py` | `eli_lab.app.launcher` |

## Rules

1. Reusable logic must not depend on Tkinter.
2. GUI code belongs in the application layer.
3. Filesystem paths use `pathlib` and shared path/config services.
4. Destructive asset operations require explicit user intent.
5. Long-running GUI operations run in workers; Tk widgets are updated through the main event loop.
6. New functionality goes under `src/eli_lab`, not as another root-level script.
7. External executables are represented as configurable backends.

## Migration strategy

The legacy scripts remain temporarily as compatibility entry points. Each tool is migrated in small, testable steps:

1. extract pure functions
2. add unit tests
3. move reusable code into the package
4. make the legacy script call the package API
5. move its GUI into `eli_lab.app`
6. remove the legacy file once the replacement is verified
