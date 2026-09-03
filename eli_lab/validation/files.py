"""Filesystem snapshot and comparison services for project validation."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SNAPSHOT_FILENAME = "folder_validation.json"


@dataclass(frozen=True, slots=True)
class FileState:
    size: int
    modified: float


def snapshot_directory(root: str | Path) -> dict[str, dict[str, Any]]:
    """Return relative file paths with size/mtime information."""
    root_path = Path(root).expanduser().resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(root_path)

    files: dict[str, dict[str, Any]] = {}
    for path in root_path.rglob("*"):
        if not path.is_file() or path.name == SNAPSHOT_FILENAME:
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        files[path.relative_to(root_path).as_posix()] = {
            "size": stat.st_size,
            "modified": stat.st_mtime,
        }
    return files


def snapshot_path(root: str | Path) -> Path:
    return Path(root).expanduser().resolve() / SNAPSHOT_FILENAME


def load_snapshot(root: str | Path) -> dict[str, Any]:
    path = snapshot_path(root)
    if not path.is_file():
        return {"version": "1.0", "files": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"version": "1.0", "files": {}}
    return data if isinstance(data, dict) else {"version": "1.0", "files": {}}


def save_snapshot(root: str | Path) -> Path:
    root_path = Path(root).expanduser().resolve()
    current = snapshot_directory(root_path)
    payload = {"version": "1.0", "files": current}
    path = snapshot_path(root_path)
    path.write_text(json.dumps(payload, indent=4), encoding="utf-8")
    return path


def compare_directory(root: str | Path) -> dict[str, str]:
    """Compare current files with the saved snapshot.

    Values are ``new``, ``modified`` or ``deleted``. Files matching the
    snapshot are omitted from the result.
    """
    current = snapshot_directory(root)
    previous = load_snapshot(root).get("files", {})
    if not isinstance(previous, dict):
        previous = {}

    status: dict[str, str] = {}
    for relative, details in current.items():
        old = previous.get(relative)
        if old is None:
            status[relative] = "new"
        elif details.get("size") != old.get("size") or details.get(
            "modified"
        ) != old.get("modified"):
            status[relative] = "modified"

    for relative in previous:
        if relative not in current:
            status[str(relative)] = "deleted"
    return status
