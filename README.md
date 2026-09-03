# eli_lab Multimedia Framework

A Python toolkit for organizing, validating, transforming, documenting, and automating the eli_lab multimedia production pipeline.

> **Status:** PySide6 production workspace. Reusable services live directly in `eli_lab/`, and the native desktop interface is implemented in `eli_lab/app/qt/`.

## What it does

The framework provides services and desktop tools for:

- project generation from standardized production profiles
- opening and scanning existing projects, including legacy and mixed hierarchies
- semantic Projects, Characters, Locations, Assets, Scenes, Scripts, and Test Scenes
- safe normalization plans for legacy files and folders, without overwriting existing destinations
- automatic project and entity metadata generation
- preset-based project README, entity catalogue, pipeline report, and compact documentation
- Blender template provisioning
- filesystem analysis and validation snapshots
- batch file renaming with previewable plans
- texture conversion and `pngquant` optimization
- task storage and historical performance analysis
- one native PySide6 desktop application

## Project-first workflow

eli_lab is designed around a production workspace rather than isolated utilities:

```text
OPEN / CREATE PROJECT
        ↓
SCAN / GENERATE STANDARD STRUCTURE
        ↓
RECOGNIZE ENTITIES
        ↓
EDIT PROJECT / ENTITY DATA
        ↓
NORMALIZE LEGACY STRUCTURE (optional, review first)
        ↓
GENERATE METADATA + DOCUMENTATION
        ↓
VALIDATE / OPTIMIZE / DIAGNOSE
        ↓
CONTINUE PRODUCTION
```

Existing projects do not have to already follow the standard. eli_lab recognizes canonical, legacy, mixed, and unknown layouts and proposes only high-confidence normalization moves automatically.

## Repository structure

```text
eli_lab-multimedia-framework/
├── eli_lab/
│   ├── core/                   # paths, config, filesystem primitives
│   ├── project/                # project models, discovery, migration, docs
│   ├── assets/                 # textures, optimization, Blender resources
│   ├── automation/             # rename planning and repeatable operations
│   ├── analysis/               # tasks and performance analysis
│   ├── validation/             # filesystem snapshots/comparisons
│   └── app/                    # registry, launcher, and PySide6 UI
├── in_progress/                # compatibility launchers for former standalone tools
├── tests/                      # service-level and pipeline tests
├── docs/                       # architecture and production pipeline notes
├── pyproject.toml
└── requirements.txt
```

There is intentionally no `src/` layer. The repository uses a simple root-level package layout so the code is easy to navigate and run directly.

## Standard production layout

The Daly-style profile used by the production workspace follows the semantic hierarchy:

```text
project/
├── Assets/
│   └── Textures/
├── Characters/
├── Locations/
├── Scripts/
├── Test Scenes/
├── Scenes/
│   └── Main Scenes/
├── Docs/
├── Renders/
└── Exports/
```

Scene and entity folders may contain their own local `assets/`, `textures/`, `references/`, or other production-specific subfolders.

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

See [docs/architecture.md](docs/architecture.md) and [docs/production-pipeline.md](docs/production-pipeline.md) for the architecture and adaptive production workflow.

## License

See [LICENSE](LICENSE).
