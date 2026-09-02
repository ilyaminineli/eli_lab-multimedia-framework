# Project subsystem migration

The project subsystem now lives directly in `eli_lab/project`.

## Current modules

- `metadata.py` — canonical `ProjectMetadata` model and JSON persistence.
- `structure.py` — compatibility facade for project structure generation.
- `templates.py` — reusable project template generation.
- `documentation.py` — project documentation generation.
- `blender.py` — Blender template provisioning.
- `validation.py` — GUI-independent project validation and reports.

## Legacy compatibility

The old Tkinter programs are temporarily stored in `in_progress/`. They are migration artifacts, not the canonical implementation. Reusable logic belongs in `eli_lab/`.

## Migration status

1. Project metadata → `eli_lab.project.metadata` ✅
2. Project structure/templates → `eli_lab.project.templates` ✅
3. Project validation/Blender provisioning → `eli_lab.project.validation` + `eli_lab.project.blender` ✅
4. Documentation generation → `eli_lab.project.documentation` ✅
5. Service-level project tests → `tests/` ✅

The remaining work is application/UI consolidation under `eli_lab.app`.

## Rules

- Project code uses `pathlib.Path`.
- Project services do not import Tkinter.
- GUI code only translates user actions into service calls.
- Validation returns structured reports rather than displaying message boxes.
- Metadata is UTF-8 JSON and uses a single canonical schema.
- No developer-specific absolute paths are permitted.
