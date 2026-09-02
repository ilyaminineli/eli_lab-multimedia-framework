"""Compatibility entry point for the PySide6 metadata tool."""
from eli_lab.app.qt.tools import MetadataTool, run_standalone


if __name__ == "__main__":
    raise SystemExit(run_standalone(MetadataTool, "ELI LAB — Project Metadata"))
