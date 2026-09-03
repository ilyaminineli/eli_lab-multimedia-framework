"""Pure historical task-performance analysis."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from typing import Mapping


@dataclass(frozen=True, slots=True)
class PerformanceReport:
    """Aggregated results suitable for a GUI, CLI, or exported report."""

    average_days_from_due: float
    task_counts_by_artist: dict[str, int]
    common_task_names: tuple[str, ...]
    common_artists: tuple[str, ...]


def _completed_delta(task: Mapping[str, str]) -> int | None:
    try:
        due_date = datetime.strptime(task["due date"], "%Y-%m-%d").date()
        status = task["status"]
        if not status.startswith("Completed on "):
            return None
        completed = datetime.strptime(
            status.removeprefix("Completed on "), "%Y-%m-%d"
        ).date()
        return (completed - due_date).days
    except (KeyError, TypeError, ValueError):
        return None


def analyze_tasks(tasks: list[Mapping[str, str]]) -> PerformanceReport:
    deltas = [delta for task in tasks if (delta := _completed_delta(task)) is not None]
    artists = Counter(task.get("assigned artist", "Unknown") for task in tasks)
    names = Counter(task.get("task name", "Unnamed") for task in tasks)

    return PerformanceReport(
        average_days_from_due=sum(deltas) / len(deltas) if deltas else 0.0,
        task_counts_by_artist=dict(artists),
        common_task_names=tuple(name for name, _ in names.most_common(5)),
        common_artists=tuple(name for name, _ in artists.most_common(5)),
    )
