"""Compatibility entry point for the PySide6 performance-analysis tool."""
from eli_lab.app.qt.tools import PerformanceTool, run_standalone


if __name__ == "__main__":
    raise SystemExit(run_standalone(PerformanceTool, "eli_lab — Performance Analysis"))
