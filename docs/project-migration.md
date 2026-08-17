# Project subsystem migration

The project subsystem is the first legacy area being moved into `src/eli_lab/project`.

## Current modules

- `metadata.py` — canonical `ProjectMetadata` model and JSON persistence.
- `structure.py` — reusable project directory generation.
- `validation.py` — GUI-independent project validation and reports.

## Legacy compatibility

The root-level Tkinter tools remain temporarily as compatibility entry points. They should call the new services instead of implementing filesystem/business logic themselves.

Migration order:

1. `project_metadata_integration.py` → `eli_lab.project.metadata` + GUI adapter.
2. `advanced_template_system.py` → `eli_lab.project.structure` + GUI adapter.
3. `project_validation.py` → `eli_lab.project.validation` + Blender template service.
4. `project_documentation_generator.py` → `eli_lab.project.documentation`.
5. Move project-related tests from GUI behavior to service-level tests.

## Rules

- Project code must use `pathlib.Path`.
- Project services must not import Tkinter.
- GUI code must only translate user actions into service calls.
- Validation returns structured reports rather than displaying message boxes.
- Metadata is UTF-8 JSON and uses a single canonical schema.
- No developer-specific absolute paths are permitted.
