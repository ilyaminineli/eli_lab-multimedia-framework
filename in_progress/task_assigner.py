"""Compatibility entry point for the PySide6 task-management tool."""
from eli_lab.app.qt.tools import TasksTool, run_standalone


if __name__ == "__main__":
    raise SystemExit(run_standalone(TasksTool, "eli_lab — Task Management"))
