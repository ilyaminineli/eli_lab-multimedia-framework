# Architecture

The framework uses a layered Python package with a native PySide6 desktop application.

## Layout

- `eli_lab/core` — configuration, paths, filesystem helpers
- `eli_lab/project` — metadata, templates, documentation, structure, validation
- `eli_lab/assets` — texture conversion, optimization, Blender templates
- `eli_lab/automation` — filename transformation and rename planning
- `eli_lab/analysis` — task storage and performance analysis
- `eli_lab/validation` — project file snapshots and comparisons
- `eli_lab/app` — application registry, launcher, and PySide6 UI
- `in_progress` — thin compatibility entry points for the former standalone tools

## GUI boundary

All active GUI code lives in `eli_lab/app/qt` and uses PySide6. Tool widgets call reusable services and do not own business or filesystem rules.

The old standalone filenames under `in_progress/` remain as tiny launchers so existing commands continue to work while the application converges on one Qt UI stack.

## Rules

1. Reusable logic must not depend on PySide6 or any other GUI toolkit.
2. GUI code belongs in the application layer.
3. Filesystem paths use `pathlib` and shared path/config services.
4. Destructive asset operations require explicit user intent.
5. Long-running operations should use Qt's worker/thread facilities rather than blocking the UI thread.
6. Validation and analysis return structured data; widgets decide how it is presented.
7. The application has one desktop entry point: `eli_lab.app.qt.application:main`.
