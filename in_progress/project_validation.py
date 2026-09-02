"""Compatibility entry point for the PySide6 project-validation tool."""
from eli_lab.app.qt.tools import ProjectValidationTool, run_standalone


if __name__ == "__main__":
    raise SystemExit(run_standalone(ProjectValidationTool, "ELI LAB — Project Validation"))
