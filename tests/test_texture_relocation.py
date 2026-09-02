from pathlib import Path

import eli_lab.production.texture_relocation as relocation
from eli_lab.production.blender_inspection import BlenderReference
from eli_lab.production.texture_relocation import TextureRelocationCandidate, plan_referenced_texture_relocations, relocate_texture_candidate


def test_plan_only_includes_actually_referenced_outside_texture(tmp_path: Path, monkeypatch) -> None:
    outside = tmp_path / "Scenes" / "textures" / "moss.png"
    outside.parent.mkdir(parents=True)
    outside.write_bytes(b"png")
    inside = tmp_path / "Assets" / "Textures" / "kept.png"
    inside.parent.mkdir(parents=True)
    inside.write_bytes(b"png")

    refs = [BlenderReference(Path("Scenes/Forest.blend"), Path("Scenes/textures/moss.png"), "image", "resolved"), BlenderReference(Path("Scenes/Forest.blend"), Path("Assets/Textures/kept.png"), "image", "resolved")]
    monkeypatch.setattr(relocation, "inspect_project", lambda root, blender_executable=None: refs)

    candidates = plan_referenced_texture_relocations(tmp_path, blender_executable="blender")
    assert len(candidates) == 1
    assert candidates[0].source == Path("Scenes/textures/moss.png")
    assert candidates[0].destination == Path("Assets/Textures/moss.png")
    assert candidates[0].blend_files == (Path("Scenes/Forest.blend"),)


def test_relocation_repairs_then_moves_and_creates_backup(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "old" / "moss.png"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"png")
    blend = tmp_path / "Scenes" / "Forest.blend"
    blend.parent.mkdir(parents=True)
    blend.write_bytes(b"blend")
    candidate = TextureRelocationCandidate(
        source=Path("old/moss.png"),
        destination=Path("Assets/Textures/moss.png"),
        blend_files=(Path("Scenes/Forest.blend"),),
        references=(BlenderReference(Path("Scenes/Forest.blend"), Path("old/moss.png"), "image", "resolved"),),
        reason="test",
        safe=True,
    )
    monkeypatch.setattr(relocation, "_repair_blend", lambda blend_file, old_path, new_path, blender_executable: True)
    monkeypatch.setattr(relocation, "record_history", lambda *args, **kwargs: None)

    result = relocate_texture_candidate(tmp_path, candidate, blender_executable="blender")
    assert result.destination == Path("Assets/Textures/moss.png")
    assert not source.exists()
    assert (tmp_path / "Assets" / "Textures" / "moss.png").read_bytes() == b"png"
    assert (result.backup_directory / "Scenes" / "Forest.blend").read_bytes() == b"blend"
    assert (result.backup_directory / "relocation.json").exists()


def test_relocation_rolls_back_when_a_reference_cannot_be_repaired(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "old" / "moss.png"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"png")
    blend = tmp_path / "Scenes" / "Forest.blend"
    blend.parent.mkdir(parents=True)
    blend.write_bytes(b"blend")
    candidate = TextureRelocationCandidate(
        source=Path("old/moss.png"),
        destination=Path("Assets/Textures/moss.png"),
        blend_files=(Path("Scenes/Forest.blend"),),
        references=(BlenderReference(Path("Scenes/Forest.blend"), Path("old/moss.png"), "image", "resolved"),),
        reason="test",
        safe=True,
    )
    monkeypatch.setattr(relocation, "_repair_blend", lambda *args: False)
    try:
        relocate_texture_candidate(tmp_path, candidate, blender_executable="blender")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected relocation to roll back")
    assert source.exists()
    assert not (tmp_path / "Assets" / "Textures" / "moss.png").exists()
    assert blend.read_bytes() == b"blend"
