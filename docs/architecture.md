# Architecture

The framework uses a deliberately simple root-level Python package. Reusable logic lives in `eli_lab/`; temporary legacy desktop programs live in `in_progress/`.

## Repository shape

```text
eli_lab-multimedia-framework/
├── eli_lab/
│   ├── core/                 # paths, config, filesystem primitives
│   ├── project/              # templates, metadata, docs, validation, Blender
│   ├── assets/               # textures, optimization, Blender resources
│   ├── automation/           # rename planning and repeatable operations
│   ├── analysis/             # tasks and performance analysis
│   └── app/                  # launcher and application registry
├── in_progress/              # legacy GUI adapters being replaced
├── tests/
├── docs/
├── pyproject.toml
└── requirements.txt
```

There is intentionally no `src/` directory. The package is directly visible at repository root.

## Dependency direction

```text
GUI / CLI
   ↓
Application adapters (`eli_lab.app`)
   ↓
Services (`project`, `assets`, `automation`, `analysis`)
   ↓
Core utilities (`eli_lab.core`)
```

Reusable services must not import Tkinter, display message boxes, or depend on the current working directory. Application code translates user actions into service calls and translates returned results into UI feedback.

## Legacy migration

The files in `in_progress/` are temporary compatibility tools. They are not the architecture; they are migration staging.

The intended end state is for each tool to have a native adapter under `eli_lab.app.tools/`, after which the corresponding legacy file can be removed.

## Safety rules

1. Preview destructive changes when practical.
2. Rename operations reject destination collisions.
3. Filesystem paths use `pathlib.Path`.
4. Long-running GUI work stays outside Tk's main thread.
5. External executables are configurable backends.
6. New reusable functionality goes under `eli_lab/`.
