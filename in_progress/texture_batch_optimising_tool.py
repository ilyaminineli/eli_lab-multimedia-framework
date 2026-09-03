"""Compatibility entry point for the PySide6 texture optimizer."""
from eli_lab.app.qt.tools import TextureOptimizationTool, run_standalone


if __name__ == "__main__":
    raise SystemExit(run_standalone(TextureOptimizationTool, "eli_lab — Texture Optimization"))
