# Architecture

eli_lab is a project-first production pipeline. The filesystem remains the source of production files, while the framework builds a semantic layer on top of it for discovery, editing, normalization, validation, and documentation.

## Layout

- `eli_lab/core` — configuration, paths, filesystem helpers
- `eli_lab/project` — project metadata, entity discovery, workspace state, templates, migration, operations, and documentation
- `eli_lab/assets` — texture conversion, optimization, Blender resources
- `eli_lab/automation` — filename transformation and rename planning
- `eli_lab/analysis` — task storage and performance analysis
- `eli_lab/validation` — filesystem snapshots and comparisons
- `eli_lab/app` — registry, launcher, and PySide6 UI
- `in_progress` — compatibility entry points for former standalone tools

## Project model

A production project is understood through six concepts:

- **Project** — the root workspace and project metadata.
- **Entity** — a character, location, asset, scene, script, or test scene discovered from the hierarchy.
- **Operation** — a repeatable action such as create, normalize, validate, optimize, or document.
- **Experiment** — temporary scripts or tests that can later become reusable operations.
- **History** — JSONL records stored under `.eli_lab/` for framework operations.
- **Documentation** — generated Markdown derived from live metadata and discovered entities.

## Adaptive projects

eli_lab does not require an existing project to already be canonical. The migration engine scans the tree, detects canonical/legacy/mixed profiles, identifies loose Blender files, loose textures, UUID-style asset folders, and scene-local asset directories, and produces a reviewable normalization plan. Only high-confidence operations are applied automatically; existing destinations are never overwritten.

## Standard generator

New projects use the Daly-style semantic profile by default through `ProjectStructure.daly()`, producing `Assets`, `Characters`, `Locations`, `Scripts`, `Test Scenes`, `Scenes/Main Scenes`, `Docs`, `Renders`, and `Exports`. Entity creation adds semantic subfolders appropriate to the entity type.

## Documentation

Documentation is preset-driven. The framework can generate a project README, entity catalogue, pipeline report, or compact overview. Entity records can also receive generated baseline descriptions which remain editable by the user.

## GUI boundary

All active GUI code lives in `eli_lab/app/qt` and uses PySide6. The Project Workspace is the project-first entry point and invokes reusable services rather than implementing business or filesystem rules itself.

## Rules

1. Reusable logic must not depend on PySide6 or another GUI toolkit.
2. GUI code belongs in the application layer.
3. Filesystem paths use `pathlib` and shared path/config services.
4. Destructive operations require explicit user intent and a reviewable plan.
5. Long-running work stays outside the Qt GUI thread.
6. Validation and analysis return structured data; widgets decide presentation.
7. Existing projects are inputs to the pipeline, not failures.
