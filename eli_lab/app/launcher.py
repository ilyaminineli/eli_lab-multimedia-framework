"""Backward-compatible launcher for the PySide6 desktop application."""

from __future__ import annotations

from .qt.application import MainWindow, main

Launcher = MainWindow

__all__ = ["Launcher", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
