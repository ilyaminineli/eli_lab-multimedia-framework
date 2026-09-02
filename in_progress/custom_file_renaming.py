"""Compatibility entry point for the PySide6 file-renaming tool."""
from eli_lab.app.qt.tools import RenameTool, run_standalone


if __name__ == "__main__":
    raise SystemExit(run_standalone(RenameTool, "ELI LAB — File Renaming"))
