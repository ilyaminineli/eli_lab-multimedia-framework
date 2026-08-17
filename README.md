# ELI LAB Multimedia Framework

A Python-based toolkit for organizing, validating, and automating the ELI LAB multimedia production pipeline.

> **Status:** active refactor toward a modular `src/eli_lab` framework. The existing GUI tools are being migrated incrementally rather than rewritten all at once.

## What it does

The framework currently contains utilities for:

- project structure and template generation
- project metadata and documentation
- file validation and project validation
- batch file renaming
- texture conversion and optimization
- task/performance analysis
- a desktop launcher for the existing tools
- Blender project templates

## Architecture

The repository is being reorganized around a shared core:

```text
eli_lab-multimedia-framework/
├── src/eli_lab/
│   ├── core/          # paths, configuration, shared infrastructure
│   ├── project/       # project structure, metadata, validation
│   ├── assets/        # textures, Blender assets, file operations
│   ├── automation/    # repeatable production operations
│   ├── analysis/      # reporting and analysis tools
│   └── app/           # GUI/CLI frontends
├── assets/
│   └── blender/
│       └── templates/
├── tests/
├── docs/
└── .github/
```

The current root-level scripts are legacy entry points. They will be moved into the package in later refactor steps while keeping their behavior intact.

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

Texture optimization can use `pngquant`. It is an external executable rather than a Python dependency and must be available on `PATH` when the optimizer is used.

## Development

The project is being stabilized in stages:

1. remove machine-specific paths and obsolete build files
2. normalize dependency and packaging metadata
3. add CI and Dependabot
4. move the tools into `src/eli_lab`
5. separate GUI code from reusable framework logic
6. introduce shared configuration, logging, errors, and filesystem services
7. add automated tests
8. add a unified CLI and application registry
9. improve packaging and release automation

Do not add new hard-coded developer paths or new standalone root-level utilities. New reusable functionality should be added under `src/eli_lab`.

## Safety principles

Production tools should prefer:

- preview before destructive operations
- explicit confirmation before deleting or replacing source files
- backups or reversible operations where practical
- platform-independent paths via `pathlib`
- structured logging instead of `print()` for framework operations
- GUI updates on Tkinter's main thread

## License

See [LICENSE](LICENSE).
