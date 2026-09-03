"""Project validation independent of the GUI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    path: Path
    message: str
    severity: str = "error"


@dataclass(frozen=True, slots=True)
class ValidationReport:
    issues: tuple[ValidationIssue, ...]

    @property
    def valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def validate_project(
    root: str | Path, required_folders: tuple[str, ...] = ()
) -> ValidationReport:
    """Validate that a project root exists and contains required directories."""
    root_path = Path(root).expanduser().resolve()
    issues: list[ValidationIssue] = []

    if not root_path.exists():
        return ValidationReport(
            (ValidationIssue(root_path, "Project root does not exist"),)
        )
    if not root_path.is_dir():
        return ValidationReport(
            (ValidationIssue(root_path, "Project root is not a directory"),)
        )

    for relative in required_folders:
        path = root_path / relative
        if not path.is_dir():
            issues.append(ValidationIssue(path, "Required directory is missing"))

    return ValidationReport(tuple(issues))
