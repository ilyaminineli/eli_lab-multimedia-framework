# ELI LAB Multimedia Framework

A Python toolkit for organizing, validating, transforming, and automating the ELI LAB multimedia production pipeline.

> **Status:** active cleanup. The reusable framework lives directly in `eli_lab/`; temporary legacy desktop programs live in `in_progress/` while they are replaced by native application modules.

## What it does

The framework provides services and desktop tools for:

- project templates, metadata, documentation, and validation
- Blender template provisioning
- filesystem analysis and file validation
- batch file renaming with previewable plans
- texture conversion and `pngquant` optimization
- task storage and historical performance analysis
- a central desktop launcher

## Repository structure

```text
eli_lab-multimedia-framework/
├── eli_lab/                    # the actual Python package
│   ├── core/                   # paths, config, filesystem primitives
│   ├── project/                # project models and services
│   ├── assets/                 # textures, optimization, Blender resources
│   ├── automation/             # rename planning and repeatable operations
│   ├── analysis/               # tasks and performance analysis
│   └── app/                    # launcher and application registry
├── in_progress/                # temporary legacy GUIs being migrated
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

## Running the launcher

After installing the package in development mode:

```bash
python -m eli_lab
```

or:

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

Keep reusable logic independent of Tkinter. Use `pathlib.Path`, return structured results from services, preview destructive changes, and keep GUI updates on Tk's main thread.

See [docs/architecture.md](docs/architecture.md) for the dependency rules and migration plan.

## License

See [LICENSE](LICENSE).
