"""Development launcher for the ELI LAB Multimedia Framework.

Run from the repository root with:

    python init.py

This intentionally keeps a simple root-level entry point for testing the
application without requiring an installed package or console-script wrapper.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eli_lab.app.launcher import main  # noqa: E402


if __name__ == "__main__":
    main()
