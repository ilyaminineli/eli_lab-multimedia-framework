"""Compatibility entry point for the PySide6 template tool.

The active implementation lives in ``eli_lab.app.qt.tools``.
"""

from eli_lab.app.qt.tools import TemplateTool, run_standalone

if __name__ == "__main__":
    raise SystemExit(run_standalone(TemplateTool, "eli_lab — Advanced Template System"))
