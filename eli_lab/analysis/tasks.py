"""Task storage model and legacy text-file compatibility."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

TASK_PREFIX = "task for "
TASK_SUFFIX = ".txt"


@dataclass(slots=True)
class Task:
    name: str
    artist: str
    due_date: date
    status: str = "Not Started"
    description: str = ""
    polls: str = ""
    assets: bool = False
    characters: bool = False
    locations: bool = False

    def to_mapping(self) -> dict[str, str]:
        return {
            "task name": self.name,
            "assigned artist": self.artist,
            "due date": self.due_date.isoformat(),
            "status": self.status,
            "description": self.description,
            "polls": self.polls,
            "assets": str(self.assets),
            "characters": str(self.characters),
            "locations": str(self.locations),
        }


def task_path(project_dir: str | Path, name: str) -> Path:
    return (
        Path(project_dir).expanduser().resolve() / f"{TASK_PREFIX}{name}{TASK_SUFFIX}"
    )


def save_task(task: Task, project_dir: str | Path) -> Path:
    directory = Path(project_dir).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    path = task_path(directory, task.name)
    lines = [f"{key}: {value}" for key, value in task.to_mapping().items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _parse(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def load_task(path: str | Path) -> Task:
    data = _parse(Path(path).expanduser().resolve())
    return Task(
        name=data["task name"],
        artist=data["assigned artist"],
        due_date=date.fromisoformat(data["due date"]),
        status=data.get("status", "Not Started"),
        description=data.get("description", ""),
        polls=data.get("polls", ""),
        assets=data.get("assets", "False") == "True",
        characters=data.get("characters", "False") == "True",
        locations=data.get("locations", "False") == "True",
    )


def list_tasks(project_dir: str | Path) -> list[Path]:
    directory = Path(project_dir).expanduser().resolve()
    if not directory.is_dir():
        return []
    return sorted(
        directory.glob(f"{TASK_PREFIX}*{TASK_SUFFIX}"),
        key=lambda path: path.name.lower(),
    )
