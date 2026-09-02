# ELI LAB Multimedia Framework

A Python toolkit for organizing, validating, transforming, and automating the ELI LAB multimedia production pipeline.

> **Status:** PySide6 migration. Reusable framework services live directly in `eli_lab/`, and all active desktop interfaces are implemented in `eli_lab/app/qt/`.

## What it does

The framework provides services and desktop tools for:

- project templates, metadata, documentation, and validation
- Blender template provisioning
- filesystem analysis and file validation snapshots
- batch file renaming with previewable plans
- texture conversion and `pngquant` optimization
- task storage and historical performance analysis
- one native PySide6 desktop application

## Repository structure

```text
eli_lab-multimedia-framework/
├── eli_lab/
│   ├── core/                   # paths, config, filesystem primitives
│   ├── project/                # project models and services
│   ├── assets/                 # textures, optimization, Blender resources
│   ├── automation/             # rename planning and repeatable operations
│   ├── analysis/               # tasks and performance analysis
│   ├── validation/             # filesystem snapshots/comparisons
│   └── app/                    # registry, launcher, and PySide6 UI
├── in_progress/                # compatibility launchers for former standalone tools
├── tests/                      # service-level tests
├── docs/                       # architecture and migration notes
├── pyproject.toml
└── requirements.txt
```

There is intentionally no `src/` layer. The repository uses a simple root-level package layout so the code is easy to navigate and run directly.

## Standard project layout

New projects use a predictable hierarchy:

```text
project/
├── assets/
│   ├── characters/
│   ├── locations/
│   ├── models/
│   └── textures/
├── scenes/
├── source/
├── renders/
├── exports/
├── docs/
└── tasks/
```

## Running the application

From the repository root:

```bash
python init.py
```

The package-native command is:

```bash
python -m eli_lab
```

Installed environments can also use:

```bash
eli-lab
```

## Installation

Python 3.10 or newer is supported.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies and the package:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

## External tools

Texture optimization can use `pngquant`. It must be available on `PATH` when optimization is used.

## Development principles

Keep reusable logic independent of the GUI toolkit. Use `pathlib.Path`, return structured results from services, preview destructive changes, and keep long-running work outside the Qt GUI thread.

See [docs/architecture.md](docs/architecture.md) for the dependency rules and [docs/project-migration.md](docs/project-migration.md) for the migration notes.

## License

See [LICENSE](LICENSE).
