# Architecture

The framework uses a layered Python package. GUI code is an adapter around reusable services rather than the place where business logic lives.

## Repository shape

```text
eli_lab-multimedia-framework/
├── src/eli_lab/
│   ├── core/                    # paths, config, filesystem primitives
│   ├── project/                 # templates, metadata, docs, validation, Blender
│   ├── assets/                  # texture services + bundled Blender templates
│   ├── automation/              # rename planning and other operations
│   ├── analysis/                # tasks and performance analysis
│   └── app/                     # GUI/CLI adapters and tool registry
├── tests/                       # service-level tests
├── docs/
└── .github/
```

## Module mapping

| Legacy tool | Package service | Application adapter |
|---|---|---|
| `advanced_template_system.py` | `eli_lab.project.templates` | legacy root GUI |
| `project_metadata_integration.py` | `eli_lab.project.metadata` | legacy root GUI |
| `project_documentation_generator.py` | `eli_lab.project.documentation` | legacy root GUI |
| `project_validation.py` | `eli_lab.project.blender` | legacy root GUI |
| `file_validation.py` | `eli_lab.core.filesystem` / project validation | legacy root GUI |
| `custom_file_renaming.py` | `eli_lab.automation.renamer` | legacy root GUI |
| `texture_batch_converter.py` | `eli_lab.assets.textures` | legacy root GUI |
| `texture_batch_optimising_tool.py` | `eli_lab.assets.optimization` | legacy root GUI |
| `task_assigner.py` | `eli_lab.analysis.tasks` | legacy root GUI |
| `historical_performance_analyzer.py` | `eli_lab.analysis.performance` | legacy root GUI |
| `init.py` | `eli_lab.app.registry` | legacy root launcher |

## Dependency direction

```text
GUI / CLI
   ↓
Application adapters
   ↓
Service modules
   ↓
Core utilities
```

Services must not import Tkinter, display message boxes, or depend on the current working directory. GUI code translates widgets into service calls and translates returned results into UI feedback.

## Safety rules

1. Preview before destructive operations when practical.
2. Destructive asset operations require explicit user intent.
3. Rename operations reject collisions and cycles before changing files.
4. Filesystem paths use `pathlib.Path`.
5. Long-running GUI work runs outside Tk's main thread.
6. External executables are configurable backends.
7. New reusable functionality goes under `src/eli_lab`.

## Migration strategy

The remaining root scripts are compatibility entry points. The next migration phase should move their widgets into `eli_lab.app` while keeping the service APIs stable:

1. convert each GUI into a small `app/tools/<tool>.py` adapter
2. remove duplicated styling and process/thread management
3. route launcher entries through the app registry
4. migrate remaining file-validation and documentation logic into services
5. delete the root compatibility scripts after a release cycle
