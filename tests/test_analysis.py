from datetime import date

from eli_lab.analysis.performance import analyze_tasks
from eli_lab.analysis.tasks import Task, load_task, save_task


def test_task_round_trip(tmp_path) -> None:
    task = Task(
        name="Lighting",
        artist="Eli",
        due_date=date(2026, 9, 10),
        description="Scene lighting",
    )
    path = save_task(task, tmp_path)
    assert load_task(path) == task


def test_performance_analysis() -> None:
    report = analyze_tasks(
        [
            {
                "task name": "Lighting",
                "assigned artist": "Eli",
                "due date": "2026-09-10",
                "status": "Completed on 2026-09-12",
            },
            {
                "task name": "Lighting",
                "assigned artist": "Eli",
                "due date": "2026-09-14",
                "status": "In Progress",
            },
            {
                "task name": "Render",
                "assigned artist": "A",
                "due date": "2026-09-10",
                "status": "Completed on 2026-09-09",
            },
        ]
    )
    assert report.average_days_from_due == 0.5
    assert report.common_task_names[0] == "Lighting"
    assert report.common_artists[0] == "Eli"
