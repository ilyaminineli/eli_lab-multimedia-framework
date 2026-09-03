"""Compatibility entry point for the PySide6 documentation tool."""
from eli_lab.app.qt.tools import DocumentationTool, run_standalone


if __name__ == "__main__":
    raise SystemExit(run_standalone(DocumentationTool, "eli_lab — Project Documentation"))
