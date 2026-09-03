"""Compatibility entry point for the PySide6 file-validation tool."""
from eli_lab.app.qt.tools import FileValidationTool, run_standalone


if __name__ == "__main__":
    raise SystemExit(run_standalone(FileValidationTool, "eli_lab — File Validation"))
