from pathlib import Path

import pytest

from eli_lab.automation.renamer import (
    add_autonumber,
    change_extension,
    convert_case,
    insert_text,
    plan_renames,
    replace_text,
)


def test_filename_transformations() -> None:
    assert add_autonumber("frame.png", 7, padding=3) == "007_frame.png"
    assert change_extension("frame.png", "jpg") == "frame.jpg"
    assert convert_case("Hello World.txt", "lower") == "hello world.txt"
    assert insert_text("file.txt", "_v2", 4) == "file_v2.txt"
    assert replace_text("draft_final.txt", "draft", "master") == "master_final.txt"


def test_rename_plan_is_non_destructive(tmp_path: Path) -> None:
    source = tmp_path / "draft.txt"
    source.write_text("x", encoding="utf-8")
    operations = plan_renames([source], lambda name: name.replace("draft", "final"))
    assert operations[0].destination == tmp_path / "final.txt"
    assert source.exists()


def test_invalid_insert_position() -> None:
    with pytest.raises(ValueError):
        insert_text("abc", "x", 4)
