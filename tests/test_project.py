from pathlib import Path

import pytest

from eli_lab.project import (
    ProjectMetadata,
    ProjectTemplate,
    create_project_structure,
    load_metadata,
    save_metadata,
    validate_project,
)


def test_project_structure_creation(tmp_path: Path) -> None:
    created = create_project_structure(tmp_path)
    assert (tmp_path / "assets" / "textures").is_dir()
    assert (tmp_path / "tasks").is_dir()
    assert len(created) == 11


def test_named_template_uses_semantic_asset_folders(tmp_path: Path) -> None:
    created = create_project_structure(
        tmp_path,
        template=ProjectTemplate(
            project_name="Demo",
            characters=("Miku",),
            locations=(("Shrine", ("references",)),),
            assets=(("Lantern", ("textures",)),),
        ),
    )
    assert (tmp_path / "Demo" / "assets" / "characters" / "Miku").is_dir()
    assert (
        tmp_path / "Demo" / "assets" / "locations" / "Shrine" / "references"
    ).is_dir()
    assert (tmp_path / "Demo" / "assets" / "models" / "Lantern" / "textures").is_dir()
    assert created


def test_metadata_round_trip(tmp_path: Path) -> None:
    metadata = ProjectMetadata(project_name="Test Project", project_code="TEST")
    path = save_metadata(metadata, tmp_path)
    loaded = load_metadata(tmp_path)
    assert path.name == "project_metadata.json"
    assert loaded == metadata


def test_invalid_metadata_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        save_metadata(ProjectMetadata(project_name="", project_code=""), tmp_path)


def test_project_validation(tmp_path: Path) -> None:
    report = validate_project(tmp_path, ("assets", "docs"))
    assert not report.valid
    (tmp_path / "assets").mkdir()
    (tmp_path / "docs").mkdir()
    assert validate_project(tmp_path, ("assets", "docs")).valid
