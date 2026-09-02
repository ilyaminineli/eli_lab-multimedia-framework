# Project migration guide

The framework has moved from a collection of standalone GUI scripts to a reusable package with a single PySide6 desktop application.

## Current structure

Reusable services live under `eli_lab/`. Active GUI widgets live under `eli_lab/app/qt/`. The `in_progress/` directory contains compatibility entry points only; those filenames now delegate to PySide6 widgets.

## Migration rules

- Project code must use `pathlib.Path`.
- Project services must not import PySide6 or any GUI toolkit.
- GUI code must only translate user actions into service calls and presentation state.
- Validation returns structured reports rather than displaying dialogs from service code.
- Metadata is UTF-8 JSON and uses a single canonical schema.
- Long operations should run outside the Qt GUI thread.

## Running the application

From the repository root:

```text
python init.py
```

The package-native equivalent is:

```text
python -m eli_lab
```

Installed environments can also use the `eli-lab` console script.

## Compatibility

The legacy filenames under `in_progress/` still work as direct launchers, but they no longer contain their own Tkinter interfaces. This keeps old workflows usable while maintaining a single PySide6 implementation.
