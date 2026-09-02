"""Shared filesystem helpers used by framework services.

This module deliberately contains no GUI code. User-facing confirmation and
progress reporting belongs in the application layer.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def iter_files(root: str | Path, *, recursive: bool = True) -> Iterator[Path]:
    """Yield files below *root* in deterministic path order."""
    root_path = Path(root).expanduser().resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(root_path)

    paths = root_path.rglob("*") if recursive else root_path.glob("*")
    for path in sorted((item for item in paths if item.is_file()), key=lambda p: p.as_posix().lower()):
        yield path


def directory_size(root: str | Path) -> int:
    """Return the total size of regular files below *root*."""
    total = 0
    for path in iter_files(root):
        if not path.is_symlink():
            total += path.stat().st_size
    return total


def read_json(path: str | Path, *, default: Any = None) -> Any:
    """Read UTF-8 JSON, optionally returning *default* when the file is absent."""
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        return default
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str | Path, data: Any) -> Path:
    """Write UTF-8 JSON, creating parent directories when necessary."""
    file_path = Path(path).expanduser().resolve()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return file_path
