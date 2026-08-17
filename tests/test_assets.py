from pathlib import Path

from PIL import Image

from eli_lab.assets import convert_texture_to_png, is_texture_file


def test_texture_extension_detection() -> None:
    assert is_texture_file("image.PNG")
    assert is_texture_file("image.tga")
    assert not is_texture_file("document.txt")


def test_texture_conversion_preserves_source_by_default(tmp_path: Path) -> None:
    source = tmp_path / "texture.jpg"
    with Image.new("RGB", (2, 2), "white") as image:
        image.save(source, "JPEG")

    result = convert_texture_to_png(source)

    assert result.success
    assert result.output == tmp_path / "texture.png"
    assert source.exists()
    assert result.output.exists()


def test_texture_conversion_can_replace_source(tmp_path: Path) -> None:
    source = tmp_path / "texture.jpg"
    with Image.new("RGB", (2, 2), "white") as image:
        image.save(source, "JPEG")

    result = convert_texture_to_png(source, replace_original=True)

    assert result.success
    assert not source.exists()
    assert result.output is not None and result.output.exists()
