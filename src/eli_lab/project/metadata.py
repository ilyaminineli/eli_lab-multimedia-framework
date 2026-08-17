"""Project metadata model and JSON persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

METADATA_FILENAME = "project_metadata.json"


@dataclass(slots=True)
class ProjectMetadata:
    """Canonical metadata shared by project-management tools."""

    project_name: str
    project_code: str
    client: str = ""
    pipeline_version: str = ""
    lead_artist: str = ""
    project_description: str = ""
    project_status: str = "In Development"
    license: str = "MIT"
    key_themes: str = ""
    contact: str = ""
    crew: str = ""
    acknowledgements: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.project_name.strip():
            errors.append("project_name is required")
        if not self.project_code.strip():
            errors.append("project_code is required")
        return errors


def metadata_path(directory: str | Path) -> Path:
    return Path(directory).expanduser().resolve() / METADATA_FILENAME


def load_metadata(directory: str | Path) -> ProjectMetadata:
    path = metadata_path(directory)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Metadata must be a JSON object: {path}")
    return ProjectMetadata(**{field: data.get(field, default) for field, default in asdict(ProjectMetadata("", "")).items()})


def save_metadata(metadata: ProjectMetadata, directory: str | Path) -> Path:
    errors = metadata.validate()
    if errors:
        raise ValueError("Invalid project metadata: " + "; ".join(errors))
    directory_path = Path(directory).expanduser().resolve()
    directory_path.mkdir(parents=True, exist_ok=True)
    path = directory_path / METADATA_FILENAME
    with path.open("w", encoding="utf-8") as handle:
        json.dump(asdict(metadata), handle, indent=4, ensure_ascii=False)
        handle.write("\n")
    return path
