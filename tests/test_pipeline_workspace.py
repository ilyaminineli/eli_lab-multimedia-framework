from pathlib import Path

from eli_lab.project.documentation_presets import build_preset_markdown
from eli_lab.project.migration import (
    apply_migration,
    build_migration_plan,
    generate_metadata,
    scan_project,
)
from eli_lab.project.workspace import scan_workspace


def test_scan_recognizes_legacy_daly_layout(tmp_path: Path) -> None:
    (tmp_path / "Characters").mkdir()
    (tmp_path / "Scenes").mkdir()
    scene = tmp_path / "Scenes" / "Tobias_Bedroom.blend"
    scene.write_bytes(b"blend")
    (tmp_path / "cover.png").write_bytes(b"png")

    scan = scan_project(tmp_path)
    assert scan.profile == "legacy-daly"
    assert scene.relative_to(tmp_path) in scan.loose_blends
    assert Path("cover.png") in scan.loose_textures


def test_legacy_scene_root_blend_has_safe_migration_plan(tmp_path: Path) -> None:
    (tmp_path / "Scenes").mkdir()
    source = tmp_path / "Scenes" / "Bedroom.blend"
    source.write_bytes(b"blend")
    plan = build_migration_plan(scan_project(tmp_path))
    assert any(
        op.source == source
        and op.destination
        == tmp_path / "Scenes" / "Main Scenes" / "Bedroom" / "Bedroom.blend"
        for op in plan.operations
    )


def test_apply_migration_never_overwrites(tmp_path: Path) -> None:
    (tmp_path / "Scenes").mkdir()
    source = tmp_path / "Scenes" / "Bedroom.blend"
    source.write_bytes(b"source")
    destination = tmp_path / "Scenes" / "Main Scenes" / "Bedroom" / "Bedroom.blend"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"existing")
    applied = apply_migration(build_migration_plan(scan_project(tmp_path)))
    assert not applied
    assert source.exists()
    assert destination.read_bytes() == b"existing"


def test_generated_metadata_and_preset_documentation(tmp_path: Path) -> None:
    (tmp_path / "Assets").mkdir()
    (tmp_path / "Characters" / "Miku").mkdir(parents=True)
    scan = scan_project(tmp_path)
    metadata = generate_metadata(scan)
    assert metadata.project_name == tmp_path.name
    summary = scan_workspace(tmp_path)
    text = build_preset_markdown(summary, "compact")
    assert tmp_path.name in text
    assert "Files" in text
