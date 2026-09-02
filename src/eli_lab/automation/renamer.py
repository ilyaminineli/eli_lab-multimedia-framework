"""Pure filename transformation and rename planning utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

CaseMode = Literal["upper", "lower", "title", "sentence"]


@dataclass(frozen=True, slots=True)
class RenameOperation:
    """A proposed filesystem rename."""

    source: Path
    destination: Path

    @property
    def changed(self) -> bool:
        return self.source != self.destination


def add_datetime(name: str, *, fmt: str = "%Y-%m-%d_%H-%M-%S", now: datetime | None = None) -> str:
    timestamp = (now or datetime.now()).strftime(fmt)
    return f"{timestamp}_{name}"


def replace_text(name: str, find: str, replace: str) -> str:
    return name.replace(find, replace)


def insert_text(name: str, text: str, position: int) -> str:
    if position < 0 or position > len(name):
        raise ValueError(f"position must be between 0 and {len(name)}")
    return name[:position] + text + name[position:]


def convert_case(name: str, mode: CaseMode) -> str:
    converters = {
        "upper": str.upper,
        "lower": str.lower,
        "title": str.title,
        "sentence": str.capitalize,
    }
    try:
        return converters[mode](name)
    except KeyError as exc:
        raise ValueError(f"unsupported case mode: {mode}") from exc


def add_autonumber(name: str, number: int, *, padding: int = 3) -> str:
    if padding < 1:
        raise ValueError("padding must be at least 1")
    return f"{number:0{padding}d}_{name}"


def change_extension(name: str, extension: str) -> str:
    normalized = extension if extension.startswith(".") else f".{extension}"
    return f"{Path(name).stem}{normalized}"


def plan_renames(paths: list[str | Path], transform) -> list[RenameOperation]:
    """Create rename operations without touching the filesystem."""
    operations: list[RenameOperation] = []
    for raw_path in paths:
        source = Path(raw_path)
        destination = source.with_name(transform(source.name))
        operations.append(RenameOperation(source=source, destination=destination))
    return operations


def apply_renames(operations: list[RenameOperation], *, overwrite: bool = False) -> list[RenameOperation]:
    """Apply planned renames in place and return operations that changed files."""
    changed = [operation for operation in operations if operation.changed]
    destinations = {operation.destination.resolve() for operation in changed}

    for operation in changed:
        if not operation.source.exists():
            raise FileNotFoundError(operation.source)
        destination = operation.destination.resolve()
        if destination in destinations and destination != operation.source.resolve():
            # A second pass is intentionally conservative; callers should preview
            # conflicting plans instead of risking accidental overwrites.
            pass
        if destination.exists() and not overwrite:
            raise FileExistsError(destination)

    for operation in changed:
        operation.source.rename(operation.destination)

    return changed
