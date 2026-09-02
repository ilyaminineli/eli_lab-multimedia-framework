# ELI LAB Multimedia Framework

A Python toolkit for organizing, validating, transforming, and automating the ELI LAB multimedia production pipeline.

> **Status:** active modularization. Reusable services now live under `src/eli_lab`; the desktop tools are being migrated incrementally as compatibility adapters.

## What it does

The framework provides services and desktop tools for:

- project templates, metadata, documentation, and validation
- Blender template provisioning
- file validation and filesystem analysis
- batch file renaming with previewable rename plans
- texture conversion and `pngquant` optimization
- task storage and historical performance analysis
- a desktop tool launcher

## Repository structure

```text
eli_lab-multimedia-framework/
├── src/eli_lab/
│   ├── core/                    # paths, config, filesystem helpers
│   ├── project/                 # templates, metadata, docs, validation, Blender
│   ├── assets/                  # texture services + packaged Blender templates
│   ├── automation/              # rename planning and other operations
│   ├── analysis/                # task and performance services
│   └── app/                     # GUI/CLI adapters and tool registry
├── tests/                       # service-level tests
├── docs/
└── .github/
```

Root-level Python files are temporary compatibility entry points. New reusable functionality belongs under `src/eli_lab`.

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

Named characters, locations, and model assets are nested under their semantic asset category instead of being spread across project-root folders.

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

Then install dependencies:

```bash
python -m pip install -r requirements.txt
```

For development:

```bash
python -m pip install -e .
```

## External tools

Texture optimization can use `pngquant`. It is an external executable rather than a Python dependency and must be available on `PATH` when optimization is used.

## Development principles

Keep reusable logic independent of Tkinter. Use `pathlib.Path` for filesystem operations, return structured results from services, preview destructive changes, and keep GUI updates on Tk's main thread.

See [docs/architecture.md](docs/architecture.md) for the migration map and dependency rules.

## License

See [LICENSE](LICENSE).
