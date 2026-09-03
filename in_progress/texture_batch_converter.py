"""Compatibility entry point for the PySide6 texture converter."""
from eli_lab.app.qt.tools import TextureConversionTool, run_standalone


if __name__ == "__main__":
    raise SystemExit(run_standalone(TextureConversionTool, "eli_lab — Texture Conversion"))
